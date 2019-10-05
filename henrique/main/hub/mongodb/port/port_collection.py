from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub


class MongoHub(object):
    pass


class PortCollection:
    NAME = "port"

    class Field:
        USER_ID = "user_id"
        DOC_ID = "doc_id"
        SPAN = "span"

    F = Field

    @classmethod
    def collection(cls, *_, **__):
        db = MongoDBHub.db()
        return db.get_collection(cls.NAME, *_, **__)

    @classmethod
    def upsert_many(cls, user_id, doc_id, span, ):
        collection = cls.get_collection()
        j_doc = {cls.F.USER_ID: user_id,
                 cls.F.DOC_ID: doc_id,
                 cls.F.SPAN: span,
                 }
        return collection.update_many(j_doc, {"$set": j_doc}, upsert=True, )

    @classmethod
    def delete_one(cls, user_id, doc_id, span):
        collection = cls.get_collection()
        j_doc = {cls.F.USER_ID: user_id,
                 cls.F.DOC_ID: doc_id,
                 cls.F.SPAN: span,
                 }
        return collection.delete_one(j_doc, )

    @classmethod
    def user_doc2list(cls, user_id, doc_id):
        collection = cls.get_collection()
        j_filter = {cls.F.USER_ID: user_id,
                    cls.F.DOC_ID: doc_id,
                    }
        return collection.find(j_filter, )

    @classmethod
    def user2list(cls, user_id):
        collection = cls.get_collection()
        j_filter = {cls.F.USER_ID: user_id,
                    }
        return collection.find(j_filter, )



    @classmethod
    def postgres2mongodb(cls):
        pass


class PortTable:
    NAME = "unchartedwatersonline_port"

    @classmethod
    def index_json(cls): return 2

