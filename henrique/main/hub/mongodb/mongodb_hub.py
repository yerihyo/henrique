from pymongo import MongoClient

from foxylib.tools.env.env_tools import EnvToolkit


class MongoDBHub:
    class Env:
        MONGO_AUTH = "MONGO_AUTH"

    @classmethod
    def uri(cls):
        return EnvToolkit.k2v(cls.Env.MONGO_AUTH)

    @classmethod
    def client(cls):
        uri = cls.uri()
        return MongoClient(uri)


