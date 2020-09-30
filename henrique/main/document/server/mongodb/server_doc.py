import logging
from operator import itemgetter as ig

from cachetools import LRUCache
from datetime import timedelta
from functools import lru_cache, partial
from future.utils import lmap
from nose.tools import assert_equal

from foxylib.tools.cache.cache_decorator import CacheDecorator
from foxylib.tools.cache.cache_manager import CacheManager
from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, l_singleton2obj
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


class ServerCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("server", *_, **__)


class ServerDocCache:
    class Constant:
        MAXSIZE = 20


class ServerNanban:
    class Field:
        DATETIME = "datetime"
        COMMAND_IN = "command_in"

    @classmethod
    def nanban2datetime(cls, nanban):
        return nanban[cls.Field.DATETIME]

    @classmethod
    def nanban2command_in(cls, nanban):
        return nanban.get(cls.Field.COMMAND_IN)


class ServerDoc:
    class Constant:
        SHELF_LIFE = timedelta(hours=4)

    class Field:
        CODENAME = "codename"
        NANBAN = "nanban"
        # COMMAND_TEXT = "command_text"
        # UPDATED_AT = "updated_at"

        @classmethod
        def set(cls):
            return {cls.CODENAME, cls.NANBAN,}

    @classmethod
    def doc2codename(cls, doc):
        return doc[cls.Field.CODENAME]

    @classmethod
    def doc2nanban(cls, doc):
        return doc[cls.Field.NANBAN]

    @classmethod
    def dict_codename2doc(cls, codenames):
        collection = ServerCollection.collection()
        mongo_query = {cls.Field.CODENAME: {"$in": codenames},
                       }
        cursor = collection.find(mongo_query)

        h_codename2doc = merge_dicts([{cls.doc2codename(doc): doc}
                                      for doc in map(MongoDBTool.bson2json, cursor)],
                                     vwrite=vwrite_no_duplicate_key)
        return h_codename2doc

    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=ServerDocCache.Constant.MAXSIZE),
                                      cachedmethod=partial(CacheDecorator.cachedmethod_each, indexes_each=[1]),
                                      )
    def codenames2docs(cls, codenames):
        h = cls.dict_codename2doc(codenames)
        doc_list = lmap(lambda x: h.get(x), codenames)
        return doc_list

    @classmethod
    def codename2doc(cls, codename):
        return l_singleton2obj(cls.codenames2docs([codename]))

    @classmethod
    def docs2upsert(cls, docs):
        logger = HenriqueLogger.func_level2logger(cls.docs2upsert, logging.DEBUG)

        def doc2pair(doc):
            doc_filter = DictTool.keys2filtered(doc, [cls.Field.CODENAME])
            return doc_filter, doc

        pair_list = lmap(doc2pair, docs)
        value_args_kwargs_list = [(doc, [[cls.doc2codename(doc)]], {}) for doc in docs]
        with CacheManager.update_cache_each(cls.codenames2docs, value_args_kwargs_list):
            collection = ServerCollection.collection()
            mongo_result = MongoDBTool.j_pair_list2upsert(collection, pair_list)

        # raise Exception({"cls.codenames2docs(lmap(cls.doc2codename, docs))": cls.codenames2docs(lmap(cls.doc2codename, docs)),
        #                  "lmap(ig(1), pair_list)": lmap(ig(1), pair_list),
        #                  })

        return mongo_result

    @classmethod
    def codenames2delete(cls, codenames):
        for codename in codenames:
            CacheManager.delete_key(cls.codenames2docs, [codename,])

        ServerCollection.collection().delete_many({ServerDoc.Field.CODENAME: {"$in": codenames}})
