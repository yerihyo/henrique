from foxylib.tools.socialmedia.discord.discord_user import DiscordUser
from khala.document.packet.packet import KhalaPacket


class Channel:
    class Codename:
        KAKAOTALK = "kakaotalk"
        DISCORD = "discord"
        SLACK = "slack"

    @classmethod
    def packet2alias(cls, packet):
        from khala.document.chatroom.chatroom import Chatroom
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))

        channel = Chatroom.chatroom2locale(chatroom)

        if channel == cls.Codename.KAKAOTALK:
            return KakaotalkChannel.packet2username(packet)

        if channel == cls.Codename.DISCORD:
            return DiscordChannel.packet2username(packet)

        raise Exception({"channel":channel})


class DiscordChannel:
    class PacketExtra:
        class Field:
            USER = "user"

        @classmethod
        def extra2discord_user(cls, extra):
            return extra.get(cls.Field.USER)

    @classmethod
    def packet2channel_user_codename(cls, packet):
        extra = KhalaPacket.packet2extra(packet)
        user = cls.PacketExtra.extra2discord_user(extra)
        user_id = DiscordUser.user2id(user)

        from khala.document.channel_user.channel_user import ChannelUser
        return ChannelUser.channel_suffix2codename(Channel.Codename.DISCORD, user_id)

    @classmethod
    def packet2username(cls, packet):
        extra = KhalaPacket.packet2extra(packet)
        user = cls.PacketExtra.extra2discord_user(extra)
        return DiscordUser.user2username(user)


class KakaotalkChannel:
    class PacketExtra:
        class Field:
            USERNAME = "username"

        @classmethod
        def extra2channel_username(cls, extra):
            return extra.get(cls.Field.USERNAME)

    @classmethod
    def packet2channel_user_codename(cls, packet):
        extra = KhalaPacket.packet2extra(packet)
        username = cls.PacketExtra.extra2channel_username(extra)

        from khala.document.channel_user.channel_user import ChannelUser
        return ChannelUser.channel_suffix2codename(Channel.Codename.DISCORD, username)


    @classmethod
    def packet2username(cls, packet):
        extra = KhalaPacket.packet2extra(packet)

        username = cls.PacketExtra.extra2channel_username(extra)
        return username

    @classmethod
    def username2channel_user_codename(cls, username):
        from khala.document.channel_user.channel_user import ChannelUser
        return ChannelUser.channel_suffix2codename(Channel.Codename.KAKAOTALK, username)
