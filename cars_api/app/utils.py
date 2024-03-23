from bson import ObjectId
from bson.errors import InvalidId


def validate_objectid(objectid_str: str) -> ObjectId | None:
    try:
        objectId = ObjectId(objectid_str)
    except InvalidId:
        return None
    else:
        return objectId
