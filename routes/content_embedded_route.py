from fastapi import APIRouter, status, Depends

from configs.security import UnauthorizedMessage, get_token
from configs.logger import logger
from configs.db import content_embedded_collection
from controllers.elastic import Elastic
from models.content_embedded_model import ContentEmbeddedModel
from schemas.content_embedded_schema import content_embedded_serializer
from utils.exception_handling import handle_exceptions
from utils.sentence_management import extract_sentence
from bson import ObjectId
import os

content_embedded_route = APIRouter(tags=["CONTENT_EMBEDDED"])
elastic = Elastic()


@content_embedded_route.get(
    "/content/embedded/find",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def find_all_embedded(
    token_auth: str = Depends(get_token)
):
    logger.info('searching history')
    def get_data(data):
        data['_id'] = str(data['_id'])
        return data
    result = [get_data(content) for content in content_embedded_collection.find({}).limit(5)]
    return {"data": {"result": result}, "message": "Success"}


@content_embedded_route.get(
    "/content/embedded/find/{id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def find_id_embedded(
    id: str,
    token_auth: str = Depends(get_token)
):
    logger.info(f'searching history {id}')
    result = content_embedded_collection.find_one({"_id": ObjectId(id)})
    result['_id'] = str(result['_id'])
    return {"data": {"result": result}, "message": "Success"}


@content_embedded_route.get(
    "/content/embedded/reset/counter",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def reset_counter(
    token_auth: str = Depends(get_token)
):
    content_embedded_collection.update_many({"counter":{"$gt":0}}, {"$set": {"counter": 0}})
    elastic.es_update_by_query(index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), 
        data_dict={"counter": 0}, query={"range": {"counter": {"gt": 0}}})
    return {"message": "Success"}


@content_embedded_route.post(
    "/content/embedded/insert",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def insert_embedded(
    body: ContentEmbeddedModel,
    token_auth: str = Depends(get_token)
):
    query = {"query": {"bool": {"must": [{"term": {"data_id": body.data_id}}, {"term": {"data_type": body.data_type}}]}}}
    if elastic.client.search(index=os.getenv('COLLECTION_CONTENT_EMBEDDED'), body=query)['hits']['hits']:
        return {"message": "Data already exists"}
    
    if body.content is not None:
        text_elements = body.split_content_token()
        content_vector = [{'vector':vector} for vector in extract_sentence(text_elements)]
    else:
        content_vector = None
    
    body = body.model_dump()
    inserted = content_embedded_collection.insert_one(body)
    if inserted:
        logger.info(f'inserted content {body}')
    else:
        return {"message": "Failed to insert data"}
    
    id = str(body.pop('_id'))
    body['content_vector'] = content_vector
    elastic.migrate_data(index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), datas=[body], ids=[id])
    body['_id'] = id
    return {"data": content_embedded_serializer(body), "message": "Success"}


@content_embedded_route.put(
    "/content/embedded/update/{id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def update_embedded(
    id: str,
    body: ContentEmbeddedModel,
    token_auth: str = Depends(get_token)
):
		
    old_data = elastic.client.search(index=os.getenv('COLLECTION_CONTENT_EMBEDDED'), body={"query": {"term": {"_id": id}}})['hits']['hits']
    if not old_data:
        return {"message": "Data not found"}
    query = {"query": {"bool": {"must": [{"term": {"data_id": body.data_id}}, {"term": {"data_type": body.data_type}}], "must_not": [{"term": {"_id": id}}]}}}
    if elastic.client.search(index=os.getenv('COLLECTION_CONTENT_EMBEDDED'), body=query)['hits']['hits']:
        return {"message": f"{body.data_type} id({body.data_id}) already exists"}
    
    old_data = old_data[0]['_source']
    if body.get_content() != old_data['content']:
        if body.content is not None:
            text_elements = body.split_content_token()
            content_vector = [{'vector':vector} for vector in extract_sentence(text_elements)]
        else:
            content_vector = None
    else:
        body.content = body.get_content()
    body = body.model_dump()
    
    updated = content_embedded_collection.update_one({"_id": ObjectId(id)}, {"$set": body})
    if updated:
        logger.info(f'updated content {body}')
    else:
        return {"message": "Failed to insert data"}

    if body['content'] != old_data['content']:
        body['content_vector'] = content_vector
    elastic.es_update_by_query(index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), query={"term": {"_id": id}}, data_dict=body)
    body['_id'] = id
    return {"message": "Success", 'body': content_embedded_serializer(body)}


@content_embedded_route.delete(
    "/content/embedded/delete/{id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    status_code=status.HTTP_200_OK,
)
@handle_exceptions
async def delete_embedded(
    id: str,
    token_auth: str = Depends(get_token)
):
    logger.info(f'deleting history {id}')
    result = None
    mg_delete = content_embedded_collection.find_one_and_delete({"_id": ObjectId(id)})
    if not mg_delete:
        logger.info(f'mongo delete {id} failed')
    else:
        result = mg_delete
        
    es_deleted, success = elastic.es_delete_by_query(index_name=os.getenv('COLLECTION_CONTENT_EMBEDDED'), query={"terms": {"_id": [id]}})
    if not success:
        logger.info(f'elast delete {id} failed')
    else:
        result = es_deleted[0]['_source']
        result['_id'] = es_deleted[0]['_id']
    return {"mongo_deleted": bool(mg_delete), "elast_deleted": bool(success), 
            "data_deleted": content_embedded_serializer(result) if result else None, "message": "Success"}
