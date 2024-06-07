from controllers.elastic import Elastic
import os

elastic = Elastic()

content_embedded_mappings = {
    "properties": {
        "content": {
            "type": "text",
            "analyzer": "thai_analyzer"
        },
        "data_id": {
            "type": "long",
            "fields": {
                "keyword": {
                    "type": "keyword"
                }
            }
        },
        "data_type": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword"
                }
            }
        },
        "name": {
            "type": "text",
            "analyzer": "thai_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword"
                }
            }
        },
        "modify_date": {
            "type": "date"
        },
        "active": {
            "type": "boolean"
        },
        "info_exist": {
            "type": "boolean"
        },
        "counter": {
            "type": "long",
            "fields": {
                "keyword": {
                    "type": "keyword"
                }
            }
        },
        "description": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword"
                }
            }
        },
        "content_vector": {
            "type": "nested",
            "properties": {
                "vector": {
                    "type": "dense_vector",
                    "dims": 384
                }
            }
        }
    }
}

content_searching_mappings = {
    "properties": {
        "question": {
            "type": "text",
            "analyzer": "thai_analyzer"
        },
        "top_k": {
            "type": "long"
        },
        "size_search": {
            "type": "long"
        },
        "boost": {
            "type": "float"
        },
        "search_date": {
            "type": "date"
        },
        "keyword": {
            "type": "boolean"
        },
        "semantic": {
            "type": "boolean"
        },
        "re_ranking": {
            "type": "boolean"
        },
        "results": {
            "type": "nested",
            "properties": {
                "id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "thai_analyzer"
                },
                "data_id": {
                    "type": "long",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "data_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "name": {
                    "type": "text",
                    "analyzer": "thai_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "modify_date": {
                    "type": "date"
                },
                "counter": {
                    "type": "long",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "url": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "score_es": {
                    "type": "float"
                },
                "rerank_score": {
                    "type": "float"
                }
            }
        }
    }
}

def create_index_es():
    elastic.create_index_es(os.getenv('COLLECTION_CONTENT_EMBEDDED'), mappings=content_embedded_mappings)
    elastic.create_index_es(os.getenv('COLLECTION_CONTENT_SEARCHING'), mappings=content_searching_mappings)