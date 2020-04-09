from foxylib.tools.socialmedia.discord.discord_user import DiscordUser
from khalalib.packet.packet import KhalaPacket


class Channel:
    class Codename:
        KAKAOTALK_UWO = "kakaotalk_uwo"
        DISCORD = "discord"
        SLACK = "slack"

    @classmethod
    def packet2user_alias(cls, packet):
        channel = KhalaPacket.packet2channel(packet)

        h_codename2func = {cls.Codename.KAKAOTALK_UWO:KakaotalkUWOChannel.packet2username,
                           cls.Codename.DISCORD: DiscordChannel.packet2username,
                           }

        f = h_codename2func.get(channel)
        if not f:
            return None

        return f(packet)


class DiscordChannel:
    class PacketExtra:
        class Field:
            USER = "user"

        @classmethod
        def extra2discord_user(cls, extra):
            return extra.get(cls.Field.USER)

    @classmethod
    def packet2channel_key(cls, packet):
        extra = KhalaPacket.packet2extra(packet)
        user = cls.PacketExtra.extra2discord_user(extra)
        user_id = DiscordUser.user2id(user)

        return user_id

    @classmethod
    def packet2username(cls, packet):
        extra = KhalaPacket.packet2extra(packet)
        user = cls.PacketExtra.extra2discord_user(extra)
        return DiscordUser.user2username(user)


class KakaotalkUWOChannel:
    class PacketExtra:
        class Field:
            USERNAME = "username"

        @classmethod
        def extra2channel_username(cls, extra):
            return extra.get(cls.Field.USERNAME)


    @classmethod
    def packet2username(cls, packet):
        extra = KhalaPacket.packet2extra(packet)

        username = cls.PacketExtra.extra2channel_username(extra)
        return username
