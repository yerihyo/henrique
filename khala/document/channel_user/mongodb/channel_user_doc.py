import sys

from cachetools import LRUCache, cached
from cachetools.keys import hashkey
from future.utils import lmap

from foxylib.tools.cache.cachetools.cachetools_tool import CachetoolsManager, CachetoolsTool
from foxylib.tools.collections.collections_tool import DictTool
from functools import lru_cache, partial

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.warmer import Warmer
from khala.document.channel.channel import Channel
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


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
    @CachetoolsManager.attach2func(cached=partial(CachetoolsTool.Decorator.cached_each, index_each=1),
                                   key=CachetoolsTool.key4classmethod(hashkey),
                                   cache=LRUCache(maxsize=ChannelUserDocCache.Constant.MAXSIZE),
                                   )
    def codenames2docs(cls, codenames):
        collection = ChannelUserCollection.collection()

        query = {ChannelUser.Field.CODENAME: {"$in": codenames}}
        doc_list = lmap(MongoDBTool.bson2json, collection.find(query))
        return doc_list

    @classmethod
    def _docs2cache(cls, docs):
        for doc in docs:
            codename = ChannelUser.doc2codename(doc)
            cls.codenames2docs.cachetools_manager.add2cache(doc, args=[codename])

    @classmethod
    def docs2upsert(cls, docs):
        def doc2pair(doc):
            doc_filter = DictTool.keys2filtered(doc, [ChannelUser.Field.CODENAME])
            return doc_filter, doc

        pair_list = lmap(doc2pair, docs)

        collection = ChannelUserCollection.collection()
        mongo_result = MongoDBTool.j_pair_list2upsert(collection, pair_list)

        cls._docs2cache(docs)

        return mongo_result






# class KakaotalkUWOChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):


WARMER.warmup()