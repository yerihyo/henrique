import sys

from cachetools import LRUCache, cached
from foxylib.tools.collections.collections_tool import DictTool
from functools import lru_cache

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.warmer import Warmer
from henrique.main.document.channel.channel import Channel, DiscordChannel, KakaotalkUWOChannel
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khalalib.packet.packet import KhalaPacket

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
        cls.key2doc.doc2cache(doc)

    class key2doc:
        MAXSIZE = 200

        @classmethod
        @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
        def cache(cls):
            return LRUCache(maxsize=cls.MAXSIZE)

        @classmethod
        def doc2cache(cls, doc):
            cache = cls.cache()
            key = ChannelUserDoc.doc2key(doc)
            cache[key] = doc

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
        KEY = "key"
        USER_ALIAS = "user_alias"
        # USER_ID = "user_id" # in the future

    @classmethod
    def doc2key(cls, doc):
        return doc[cls.Field.KEY]

    @classmethod
    def doc2user_alias(cls, doc):
        return doc.get(cls.Field.USER_ALIAS)

    @classmethod
    @cached(ChannelUserDocCache.key2doc.cache())
    def key2doc(cls, key):
        collection = ChannelUserCollection.collection()
        doc = MongoDBTool.bson2json(collection.find_one({cls.Field.KEY: key}))
        return doc

    @classmethod
    def packet2key(cls, packet):
        channel = KhalaPacket.packet2channel(packet)
        channel_key = cls.packet2channel_key(packet)
        return "-".join([channel, channel_key])

    @classmethod
    def packet2channel_key(cls, packet,):
        channel = KhalaPacket.packet2channel(packet)

        if channel == Channel.Codename.DISCORD:
            return DiscordChannel.packet2channel_key(packet)

        if channel == Channel.Codename.KAKAOTALK_UWO:
            return KakaotalkUWOChannel.packet2username(packet)

        raise NotImplementedError({"channel": channel})

    @classmethod
    def packet2upsert(cls, packet):
        doc = {cls.Field.CHANNEL: KhalaPacket.packet2channel(packet),
               cls.Field.KEY: cls.packet2key(packet),
               cls.Field.USER_ALIAS: Channel.packet2user_alias(packet),
               }

        doc_filter = DictTool.keys2filtered(doc, [cls.Field.KEY])

        collection = ChannelUserCollection.collection()
        mongo_result = MongoDBTool.j_pair_list2upsert(collection, [(doc_filter, doc)])
        return mongo_result

    @classmethod
    def packet2doc(cls, packet):
        return cls.key2doc(cls.packet2key(packet))



# class KakaotalkChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):


WARMER.warmup()