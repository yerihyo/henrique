from foxylib.tools.socialmedia.discord.discord_user import DiscordUser
from khala.document.packet.packet import KhalaPacket


class Channel:
    class Codename:
        KAKAOTALK_UWO = "kakaotalk_uwo"
        DISCORD = "discord"
        SLACK = "slack"

    @classmethod
    def packet2codename(cls, packet):
        from khala.document.chatroom.chatroom import Chatroom
        chatroom_codename = KhalaPacket.packet2chatroom(packet)
        codename = Chatroom.codename2channel(chatroom_codename)
        return codename

    @classmethod
    def packet2alias(cls, packet):
        from khala.singleton.messenger.discord.internal.packet_discord import PacketDiscord

        # codename = cls.packet2codename(packet)
        return KhalaPacket.packet2sender_name(packet)

        # if codename == cls.Codename.KAKAOTALK_UWO:
        #     return KakaotalkUWOChannel.packet2username(packet)
        #
        # if codename == cls.Codename.DISCORD:
        #     return PacketDiscord.packet2username(packet)
        #
        # raise Exception({"channel":codename})




class KakaotalkUWOChannel:
    # class PacketExtra:
    #     class Field:
    #         USERNAME = "username"
    #
    #     @classmethod
    #     def extra2channel_username(cls, extra):
    #         return extra.get(cls.Field.USERNAME)
    #
    # @classmethod
    # def packet2channel_user_codename(cls, packet):
    #     sender_name = KhalaPacket.packet2sender_name(packet)
    #     return cls.username2channel_user_codename(sender_name)

    # @classmethod
    # def packet2username(cls, packet):
    #     return KhalaPacket.packet2sender_name(packet)

    @classmethod
    def username2channel_user_codename(cls, username):
        from khala.document.channel_user.channel_user import ChannelUser
        return ChannelUser.channel_suffix2codename(Channel.Codename.KAKAOTALK_UWO, username)
