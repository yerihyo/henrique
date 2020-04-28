import logging

from cachetools import cached, LRUCache
from cachetools.keys import hashkey
from functools import lru_cache, partial
from future.utils import lmap
from nose.tools import assert_equal

from foxylib.tools.cache.cache_tool import CacheTool
from foxylib.tools.cache.cachetools.cachetools_tool import CachetoolsTool, CachetoolsManager
from foxylib.tools.collections.collections_tool import DictTool, l_singleton2obj, vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb
from khala.document.channel.channel import KakaotalkUWOChannel, Channel
from khala.singleton.logger.khala_logger import KhalaLogger


class ChatroomCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("chatroom", *_, **__)


class ChatroomCache:
    class Constant:
        MAXSIZE = 256


class Chatroom:
    Cache = ChatroomCache

    class Constant:
        DELIM = "-"

    class Field:
        CHANNEL = "channel"
        CODENAME = "codename"
        # NAME = "name"
        LOCALE = "locale"
        # EXTRA = "extra"

    # @classmethod
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def dict_codename2chatroom(cls):
    #     from khala.document.chatroom.googlesheets.chatroom_googlesheets import ChatroomGooglesheets
    #     return ChatroomGooglesheets.dict_codename2chatroom()

    @classmethod
    def codename2chatroom(cls, codename):
        logger = HenriqueLogger.func_level2logger(cls.codename2chatroom, logging.DEBUG)
        logger.debug({"codename": codename})

        return l_singleton2obj(cls.codenames2chatrooms([codename]))

    @classmethod
    @CachetoolsManager.attach2func(cached=partial(CachetoolsTool.Decorator.cached_each, index_each=1),
                                   key=CachetoolsTool.key4classmethod(hashkey),
                                   cache=LRUCache(maxsize=ChatroomCache.Constant.MAXSIZE),
                                   )
    def codenames2chatrooms(cls, codenames):
        logger = KhalaLogger.func_level2logger(cls.codenames2chatrooms, logging.DEBUG)

        collection = ChatroomCollection.collection()
        if codenames is not None:
            cursor = collection.find({cls.Field.CODENAME: {"$in": codenames}})
        else:
            cursor = collection.find()

        h_codename2doc = merge_dicts([{Chatroom.chatroom2codename(doc): doc}
                                      for doc in map(MongoDBTool.bson2json, cursor)],
                                     vwrite=vwrite_no_duplicate_key)

        doc_list = lmap(h_codename2doc.get, codenames)

        logger.debug({"codenames":codenames,
                      "doc_list":doc_list,
                      })
        assert_equal(len(codenames), len(doc_list))
        return doc_list

    @classmethod
    def add_chatroom2cache(cls, chatroom):
        codename = cls.chatroom2codename(chatroom)
        cls.codenames2chatrooms.cachetools_manager.add2cache(chatroom, [cls, codename,])

    @classmethod
    def chatroom2codename(cls, chatroom):
        return chatroom[cls.Field.CODENAME]

    @classmethod
    def chatroom2locale(cls, chatroom):
        return chatroom[cls.Field.LOCALE]

    @classmethod
    def codename2channel(cls, codename):
        return codename.split(cls.Constant.DELIM)[0]

    @classmethod
    def chatroom2channel(cls, chatroom):
        codename = cls.chatroom2codename(chatroom)
        return cls.codename2channel(codename)

    @classmethod
    def channel_suffix2codename(cls, channel_codename, chatroom_name):
        return cls.Constant.DELIM.join([channel_codename, chatroom_name])

    @classmethod
    def chatrooms2upsert(cls, chatrooms):
        from khala.document.chatroom.mongodb.chatroom_doc import ChatroomDoc
        ChatroomDoc.docs2upsert(chatrooms)
        # return chatroom


class KakaotalkUWOChatroom:
    NAME = "uwo"

    @classmethod
    def codename(cls):
        return Chatroom.channel_suffix2codename(Channel.Codename.KAKAOTALK_UWO, cls.NAME)
