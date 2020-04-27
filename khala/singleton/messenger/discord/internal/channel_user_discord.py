import logging

from khala.document.channel.channel import Channel
from khala.document.channel_user.channel_user import ChannelUser
from khala.singleton.logger.khala_logger import KhalaLogger
from khala.singleton.messenger.discord.internal.packet_discord import PacketDiscord


class ChannelUserDiscord:
    @classmethod
    def message2codename(cls, message):
        return ChannelUser.channel_suffix2codename(Channel.Codename.DISCORD, str(message.author.id))

    @classmethod
    def message2channel_user(cls, message):
        logger = KhalaLogger.func_level2logger(cls.message2channel_user, logging.DEBUG)

        codename = cls.message2codename(message)
        alias = PacketDiscord.message2sender_name(message)

        doc = {ChannelUser.Field.CHANNEL: Channel.Codename.DISCORD,
               ChannelUser.Field.CODENAME: codename,
               ChannelUser.Field.ALIAS: alias
               }

        logger.debug({"message": message,
                      "doc": doc,
                      })

        return doc
