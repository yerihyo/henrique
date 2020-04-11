import sys

from cachetools import LRUCache, cached
from foxylib.tools.collections.collections_tool import DictTool
from functools import lru_cache

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.warmer import Warmer
from khala.document.channel.channel import Channel, DiscordChannel, KakaotalkChannel
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khala.document.channel_user.channel_user import ChannelUser
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
    @classmethod
    def doc2cache(cls, doc):
        cls.codename2doc.doc2cache(doc)

    class codename2doc:
        MAXSIZE = 200

        @classmethod
        @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
        def cache(cls):
            return LRUCache(maxsize=cls.MAXSIZE)

        @classmethod
        def doc2cache(cls, doc):
            cache = cls.cache()
            codename = ChannelUserDoc.doc2codename(doc)
            cache[codename] = doc

        @classmethod
        @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
        def collection2cache(cls):
            collection = ChannelUserCollection.collection()
            doc_iter = map(MongoDBTool.bson2json, collection.find({}))
            for doc in IterTool.head(cls.MAXSIZE, doc_iter):
                cls.doc2cache(doc)


class ChannelUserDoc:
    Cache = ChannelUserDocCache

    class Field:
        CHANNEL = "channel"
        CODENAME = "codename"
        ALIAS = "alias"
        # USER_ID = "user_id" # in the future

    @classmethod
    def doc2codename(cls, doc):
        return doc[cls.Field.CODENAME]

    @classmethod
    @cached(ChannelUserDocCache.codename2doc.cache())
    def codename2doc(cls, codename):
        collection = ChannelUserCollection.collection()
        doc = MongoDBTool.bson2json(collection.find_one({cls.Field.CODENAME: codename}))
        return doc

    @classmethod
    def packet2upsert(cls, packet):

        doc = cls.packet2doc(packet)
        doc_filter = DictTool.keys2filtered(doc, [cls.Field.CODENAME])

        collection = ChannelUserCollection.collection()
        mongo_result = MongoDBTool.j_pair_list2upsert(collection, [(doc_filter, doc)])
        return mongo_result

    @classmethod
    def packet2doc(cls, packet):
        codename = ChannelUser.packet2codename(packet)
        channel = KhalaPacket.packet2channel(packet)

        channel = KhalaPacket.packet2channel(packet)
        if channel == Channel.Codename.DISCORD:
            return DiscordChannel.packet2channel_user_doc(packet)

        if channel == Channel.Codename.KAKAOTALK:
            return KakaotalkChannel.packet2channel_user_doc(packet)

        raise NotImplementedError({"channel":channel})





# class KakaotalkChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):


WARMER.warmup()