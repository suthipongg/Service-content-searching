from fastapi import APIRouter, status, Depends, BackgroundTasks

from configs.security import UnauthorizedMessage, get_token
from configs.logger import logger
from configs.db import content_searching_collection, content_embedded_collection
from controllers.elastic import Elastic
from models.content_search_model import ContentSearchModel
from schemas.content_search_schema import contents_serializer
from utils.exception_handling import handle_exceptions
from utils.sentence_management import semantic_search_token_sep, extract_sentence, re_ranking_question
from bson import ObjectId
import os

content_search_route = APIRouter(tags=["CONTENT_SEARCH"])
elastic = Elastic()


@content_search_route.get(
    "/content/search/history",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def find_all_history(
    token_auth: str = Depends(get_token)
):
    logger.info('searching history')
    def get_data(data):
        data['_id'] = str(data['_id'])
        return data
    result = [get_data(content) for content in content_searching_collection.find({}).limit(5)]
    return {"data": {"result": result}, "message": "Success"}


@content_search_route.get(
    "/content/search/history/{id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def find_id_history(
    id: str,
    token_auth: str = Depends(get_token)
):
    logger.info(f'searching history {id}')
    result = content_searching_collection.find_one({"_id": ObjectId(id)})
    result['_id'] = str(result['_id'])
    return {"data": {"result": result}, "message": "Success"}


@content_search_route.delete(
    "/content/search/history/delete/{id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def delete_id_history(
    id: str,
    background_tasks: BackgroundTasks,
    token_auth: str = Depends(get_token)
):
    logger.info(f'deleting history {id}')
    result = None
    mg_delete = content_searching_collection.find_one_and_delete({"_id": ObjectId(id)})
    if not mg_delete:
        logger.info(f'mongo delete history {id} failed')
    else:
        background_tasks.add_task(content_embedded_collection.update_many, 
            filter = {"_id": {"$in": [ObjectId(content['id']) for content in mg_delete['results']]}},
            update = {"$inc": {"counter": -1}})
        mg_delete['id'] = str(mg_delete.pop('_id'))
        result = mg_delete
    
    es_deleted, success = elastic.es_delete_by_query(index_name=os.getenv('COLLECTION_CONTENT_SEARCHING'), query={"terms": {"_id": [id]}})
    if not success:
        logger.info(f'elast delete history {id} failed')
    else:
        background_tasks.add_task(elastic.es_update_by_query, index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), query={"terms": 
            {"_id": [content['id'] for content in es_deleted[0]['_source']['results']]}}, data_dict={"counter-":1})
        result = es_deleted[0]['_source']
        result['id'] = es_deleted[0]['_id']
    return {"mongo_deleted": bool(mg_delete), "elast_deleted": bool(success), "data_deleted": result}


@content_search_route.post(
    "/content/search/product",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def search_product(
    background_tasks: BackgroundTasks,
    body: ContentSearchModel,
    keyword: bool = True,
    semantic: bool = True,
    re_ranking: bool = False,
    token_auth: str = Depends(get_token)
):
    logger.info('searching product')
    body = body.model_dump()

    arg = {"size_search": body['size_search'], "boost": body['boost']}
    if semantic:
        logger.info('semantic searching')
        question_vector = extract_sentence(body['question'])
        arg['query_vector'] = question_vector
    if keyword:
        logger.info('keyword searching')
        arg['question'] = body['question']
    search_result = semantic_search_token_sep(**arg)
    logger.info('elastic searching success')
    
    if re_ranking == True:
        logger.info('re-ranking searching')
        search_result = re_ranking_question(body['question'], search_result, body['top_k'])
        logger.info('re-ranking success')
    else:
        search_result = search_result[:body['top_k']]
    search_result = contents_serializer(search_result)
    
    background_tasks.add_task(content_embedded_collection.update_many, 
        filter = {"_id": {"$in": [ObjectId(content['id']) for content in search_result]}},
        update = {"$inc": {"counter": 1}})
    background_tasks.add_task(elastic.es_update_by_query, index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), query={"terms": 
        {"_id": [content['id'] for content in search_result]}}, data_dict={"counter+":1})
    
    logger.info('insert searching product')
    body.update({"keyword": keyword, "semantic": semantic, "re_ranking": re_ranking, "results": search_result})
    inserted = content_searching_collection.insert_one(body)
    if not inserted:
        logger.error('insert searching product failed')
        return {"data": {"result": search_result}, "message": "Failed"}
    elastic.migrate_data(index_name=os.getenv('COLLECTION_CONTENT_SEARCHING'), datas=[body], ids=[str(body.pop('_id'))])
    logger.info('searching product success')
    
    return {"data": {"result": search_result}, "message": "Success"}

