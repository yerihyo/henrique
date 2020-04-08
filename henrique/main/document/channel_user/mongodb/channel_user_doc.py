from functools import lru_cache

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


class ChannelUserCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("channel_user", *_, **__)


class ChannelUserDoc:
    class Field:
        CHANNEL = "channel"
        USER = "user"
        DATA = "data"
    F = Field


# class KakaotalkChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):

