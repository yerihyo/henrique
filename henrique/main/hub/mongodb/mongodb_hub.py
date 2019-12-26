from pymongo import MongoClient

from foxylib.tools.env.env_tool import EnvTool


class MongoDBHub:
    class Env:
        MONGO_URI = "MONGO_URI"
        # MONGODB_SUFFIX = "MONGODB_SUFFIX"
        MONGO_DBNAME = "MONGO_DBNAME"

    @classmethod
    def uri(cls):
        return EnvTool.k2v(cls.Env.MONGO_URI)

    @classmethod
    def client(cls):
        uri = cls.uri()
        return MongoClient(uri)

    @classmethod
    def db(cls):
        client = cls.client()
        dbname = EnvTool.k2v(cls.Env.MONGO_DBNAME)
        return client[dbname]

    @classmethod
    def j_iter2insert(cls, collection, j_iter):
        return collection.insert_many(list(j_iter))