from pymongo import MongoClient

from foxylib.tools.env.env_tools import EnvToolkit


class MongoDBHub:
    class Env:
        MONGODB_AUTH = "MONGODB_AUTH"
        MONGODB_SUFFIX = "MONGODB_SUFFIX"
        MONGODB_DBNAME = "MONGODB_DBNAME"

    @classmethod
    def uri(cls):
        auth = EnvToolkit.k2v(cls.Env.MONGODB_AUTH)
        suffix = EnvToolkit.k2v(cls.Env.MONGODB_SUFFIX)
        return "{}?{}".format(auth, suffix)

    @classmethod
    def client(cls):
        uri = cls.uri()
        return MongoClient(uri)

    @classmethod
    def db(cls):
        client = cls.client()
        dbname = EnvToolkit.k2v(cls.Env.MONGODB_DBNAME)
        return client[dbname]

    @classmethod
    def str_pair2collection(cls, str_db, str_collection):
        client = cls.client()
        db = client[str_db]
        collection = db[str_collection]
        return collection

    @classmethod
    def j_iter2insert(cls, collection, j_iter):
        return collection.insert_many(list(j_iter))