import os

def content_serializer(content) -> dict:
    result = {
        'id':content["_id"],
        'data_id':content["_source"]["data_id"],
        'data_type':content["_source"]["data_type"],
        'name':content["_source"]["name"],
        'content':content["_source"]["content"],
        'modify_date':content["_source"]["modify_date"],
        'counter':content["_source"]["counter"],
        'description':content["_source"]["description"],
        'score_es': content['_score'],
        'url':f'{os.getenv("HEADER_PRODUCT_URL")}/product/{content["_source"]["data_id"]}',
    }
    if 'rerank_score' in content:
        result['rerank_score'] = content['rerank_score']
    return result


def contents_serializer(contents) -> list:
    return [content_serializer(content) for content in contents]
