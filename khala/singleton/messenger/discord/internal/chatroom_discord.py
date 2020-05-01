import logging

from khala.document.channel.channel import Channel
from khala.document.chatroom.chatroom import Chatroom
from khala.khala import Khala
from khala.singleton.logger.khala_logger import KhalaLogger


class ChatroomDiscordExtra:
    class Field:
        CHANNEL_ID = "channel_id"

    @classmethod
    def message2extra(cls, message):
        return {cls.Field.CHANNEL_ID: message.channel.id}


class ChatroomDiscord:
    Extra = ChatroomDiscordExtra

    @classmethod
    def message2codename(cls, message):
        return Chatroom.channel_suffix2codename(Channel.Codename.DISCORD, str(message.channel.id))

    @classmethod
    def message2chatroom(cls, message):
        logger = KhalaLogger.func_level2logger(cls.message2chatroom, logging.DEBUG)

        codename = cls.message2codename(message)
        chatroom = {Chatroom.Field.CHANNEL: Channel.Codename.DISCORD,
                    Chatroom.Field.CODENAME: codename,
                    # Chatroom.Field.EXTRA: ChatroomDiscord.Extra.message2extra(message),
                    Chatroom.Field.LOCALE: Khala.Default.LOCALE,
                    }
        logger.debug({"message": message,
                      "chatroom": chatroom,
                      })
        return chatroom
