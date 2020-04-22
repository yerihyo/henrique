from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from khala.document.channel.channel import KakaotalkUWOChannel, Channel


class Chatroom:
    class Constant:
        DELIM = "-"

    class Field:
        CHANNEL = "channel"
        CODENAME = "codename"
        NAME = "name"
        LOCALE = "locale"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2chatroom(cls):
        from khala.document.chatroom.googlesheets.chatroom_googlesheets import ChatroomGooglesheets
        return ChatroomGooglesheets.dict_codename2chatroom()

    @classmethod
    def codename2chatroom(cls, codename):
        return cls.dict_codename2chatroom().get(codename)

    @classmethod
    def chatroom2codename(cls, chatroom):
        return chatroom[cls.Field.CODENAME]

    @classmethod
    def chatroom2locale(cls, chatroom):
        return chatroom[cls.Field.LOCALE]

    @classmethod
    def chatroom2channel(cls, chatroom):
        codename = cls.chatroom2codename(chatroom)
        return codename.split(cls.Constant.DELIM)[0]


class KakaotalkUWOChatroom:
    CODENAME = "kakaotalk_uwo-uwo"
