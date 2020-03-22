from functools import lru_cache

from pymongo import MongoClient

from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv


class HenriqueMongodb:
    class Env:
        MONGO_URI = "MONGO_URI"
        # MONGODB_SUFFIX = "MONGODB_SUFFIX"
        MONGO_DBNAME = "MONGO_DBNAME"

    @classmethod
    def uri(cls):
        return HenriqueEnv.key2value(cls.Env.MONGO_URI)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def client(cls):
        uri = cls.uri()
        return MongoClient(uri)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def db(cls):
        client = cls.client()
        dbname = HenriqueEnv.key2value(cls.Env.MONGO_DBNAME)
        return client[dbname]

    @classmethod
    def j_iter2insert(cls, collection, j_iter):
        return collection.insert_many(list(j_iter))