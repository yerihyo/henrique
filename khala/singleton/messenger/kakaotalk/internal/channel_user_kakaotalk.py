import logging

from khala.document.channel.channel import Channel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.packet.packet import KhalaPacket
from khala.singleton.logger.khala_logger import KhalaLogger
from khala.singleton.messenger.discord.internal.packet_discord import PacketDiscord


class ChannelUserKakaotalk:
    @classmethod
    def sender_name2codename(cls, sender_name):
        return ChannelUser.channel_suffix2codename(Channel.Codename.KAKAOTALK_UWO, sender_name)

    @classmethod
    def sender_name2channel_user(cls, sender_name):
        logger = KhalaLogger.func_level2logger(cls.sender_name2channel_user, logging.DEBUG)

        codename = cls.sender_name2codename(sender_name)

        doc = {ChannelUser.Field.CHANNEL: Channel.Codename.KAKAOTALK_UWO,
               ChannelUser.Field.CODENAME: codename,
               ChannelUser.Field.ALIAS: sender_name
               }

        logger.debug({"sender_name": sender_name,
                      "doc": doc,
                      })

        return doc
