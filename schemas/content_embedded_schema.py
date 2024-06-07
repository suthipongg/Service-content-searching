def content_embedded_serializer(content) -> dict:
    result = {
        'id':str(content["_id"]),
        'data_id':content["data_id"],
        'data_type':content["data_type"],
        'name':content["name"],
        'content':content["content"],
        'modify_date':content["modify_date"],
        'counter':content["counter"],
        'description':content["description"],
        'active':content["active"],
        'info_exist':content["info_exist"],
    }
    return result


def contents_embedded_serializer(contents) -> list:
    return [content_embedded_serializer(content) for content in contents]
