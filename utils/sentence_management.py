from controllers.elastic import Elastic
import requests, json, os
from configs.logger import logger

elastic = Elastic()

def semantic_search_token_sep(question=None, query_vector=None, size_search=20, boost=0.018):
    should_search = []
    if query_vector is not None:
        should_search.append({
            "nested": {
                "path": "content_vector",
                "score_mode": "max", 
                "query": {
                    "function_score": {
                        "script_score": {
                            "script": {
                                "source": "dotProduct(params.query_vector, 'content_vector.vector')/2+0.5",
                                "params": {"query_vector": query_vector}
                            }
                        }
                    }
                }
            }
        })
    if question is not None:
        should_search.append({
            "multi_match": {
                "query": question,
                "boost": boost,
                "fields": ["content"]
            }
        })
    query_data = {
        "function_score": {
            "query": {
                "bool": {
                    "must": {
                        "exists": {
                            "field": "content"
                        }
                    },
                    "filter": [
                        {"term": {"active": True}},
                        {"term": {"info_exist": True}}
                    ],
                    "should": should_search
                }
            },
        }
    }
    source_excludes = ["content_vector", "active", "info_exist"]
    return elastic.client.search(index=os.getenv('COLLECTION_CONTENT_EMBEDDED'), 
            query=query_data, size=size_search, _source_excludes=source_excludes)['hits']['hits']
    

def extract_sentence(sentence):
    url_sentence = os.getenv("EXTRACT_SENTENCE_API_URL", "")
    headers_sentence = {"Content-Type": "application/json", "Authorization": "Bearer " + os.getenv("EXTRACT_SENTENCE_API_TOKEN")}
    payload_sentence = json.dumps({"sentence": sentence})
    response_sentence = requests.request("POST", url_sentence, headers=headers_sentence, data=payload_sentence)
    question_vector = response_sentence.json()
    if question_vector['is_exist']:
        question_vector = question_vector['result']
    question_vector = question_vector['sentence_vector']
    return question_vector

def re_ranking_question(question, search_result, top_k):
    logger.info('re-ranking product')
    url_rank = os.getenv("RE_RANKING_API_URL", "")
    headers_rank = {"Content-Type": "application/json", "Authorization": "Bearer " + os.getenv("RE_RANKING_API_TOKEN")}
    payload_rank = json.dumps({"content": [cont['_source']['content'] for cont in search_result], "question": question, "top_k": top_k})
    response_rank = requests.request("POST", url_rank, headers=headers_rank, data=payload_rank)
    output = response_rank.json()
    def set_score(x):
        search_result[x]['rerank_score'] = output['rerank_score'].pop(0)
        return search_result[x]
    search_result = list(map(lambda x: set_score(x), output['rerank_index']))
    return search_result
