import logging
import sys

from cachetools import LRUCache
from functools import lru_cache, partial
from future.utils import lmap

from foxylib.tools.cache.cache_decorator import CacheDecorator
from foxylib.tools.cache.cache_manager import CacheManager
from foxylib.tools.collections.collections_tool import DictTool, vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb
from khala.document.channel_user.channel_user import ChannelUser
from khala.singleton.logger.khala_logger import KhalaLogger

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class ChannelUserCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("channel_user", *_, **__)


class ChannelUserDocCache:
    class Constant:
        MAXSIZE = 200

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    def warmer(cls,):
        collection = ChannelUserCollection.collection()
        docs = map(MongoDBTool.bson2json, collection.find())
        ChannelUserDoc._docs2cache(docs)


class ChannelUserDoc:
    Cache = ChannelUserDocCache

    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=ChannelUserDocCache.Constant.MAXSIZE),
                                      cachedmethod=partial(CacheDecorator.cachedmethod_each, indexes_each=[1]),
                                      )
    def codenames2docs(cls, codenames):
        collection = ChannelUserCollection.collection()

        query = {ChannelUser.Field.CODENAME: {"$in": codenames}}
        cursor = collection.find(query)
        h_codename2doc = merge_dicts([{ChannelUser.channel_user2codename(doc): doc}
                                      for doc in map(MongoDBTool.bson2json, cursor)],
                                     vwrite=vwrite_no_duplicate_key)

        doc_list = lmap(h_codename2doc.get, codenames)
        return doc_list

    @classmethod
    def _docs2cache(cls, docs):
        logger = KhalaLogger.func_level2logger(cls._docs2cache, logging.DEBUG)

        for doc in docs:
            codename = ChannelUser.channel_user2codename(doc)
            CacheManager.add2cache(cls.codenames2docs, doc, args=[codename])

    @classmethod
    def docs2upsert(cls, docs):
        logger = KhalaLogger.func_level2logger(cls.docs2upsert, logging.DEBUG)

        def doc2pair(doc):
            doc_filter = DictTool.keys2filtered(doc, [ChannelUser.Field.CODENAME])
            return doc_filter, doc

        pair_list = lmap(doc2pair, docs)


        collection = ChannelUserCollection.collection()
        mongo_result = MongoDBTool.j_pair_list2upsert(collection, pair_list)

        logger.debug({"mongo_result.bulk_api_result":mongo_result.bulk_api_result,})

        # raise Exception({"docs": docs,
        #                  "pair_list": pair_list ,
        #                  "mongo_result.bulk_api_result":mongo_result.bulk_api_result,
        #                  })

        cls._docs2cache(docs)

        return mongo_result






# class KakaotalkUWOChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):


WARMER.warmup()