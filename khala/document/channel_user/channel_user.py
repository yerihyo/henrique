import sys

from foxylib.tools.function.warmer import Warmer
from khala.document.channel.channel import Channel, KakaotalkUWOChannel
from khala.document.packet.packet import KhalaPacket

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class ChannelUser:
    class Constant:
        DELIM = "-"

    class Field:
        CHANNEL = "channel"
        CODENAME = "codename"
        ALIAS = "alias"
        # USER_ID = "user_id" # in the future

    @classmethod
    def doc2codename(cls, doc):
        return doc[cls.Field.CODENAME]

    @classmethod
    def channel_user2alias(cls, channel_user):
        return channel_user.get(cls.Field.ALIAS)

    @classmethod
    def codenames2channel_users(cls, codenames):
        from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc
        return ChannelUserDoc.codenames2docs(codenames)

    # @classmethod
    # def packet2codename(cls, packet):
    #     from khala.document.chatroom.chatroom import Chatroom
    #     from khala.singleton.messenger.discord.internal.packet_discord import PacketDiscord
    #
    #     chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
    #
    #     channel = Chatroom.chatroom2channel(chatroom)
    #
    #     if channel == Channel.Codename.DISCORD:
    #         return PacketDiscord.packet2channel_user_codename(packet)
    #
    #     if channel == Channel.Codename.KAKAOTALK_UWO:
    #         return KakaotalkUWOChannel.packet2channel_user_codename(packet)
    #
    #     raise NotImplementedError({"channel": channel})

    # @classmethod
    # def packet2upsert(cls, packet):
    #     from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc
    #
    #     return ChannelUserDoc.packet2upsert(packet)

    # @classmethod
    # def packet2channel_user(cls, packet):
    #     from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc
    #
    #     codename = cls.packet2codename(packet)
    #     return ChannelUserDoc.codename2doc(codename)

    @classmethod
    def channel_suffix2codename(cls, channel, suffix):
        return cls.Constant.DELIM.join([channel, suffix])

    @classmethod
    def channel_users2upsert(cls, channel_users):
        from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc
        ChannelUserDoc.docs2upsert(channel_users)


# class KakaotalkUWOChannelUserDoc:
#     @classmethod
#     def username2doc(cls, username):


WARMER.warmup()