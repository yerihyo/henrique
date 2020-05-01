from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket


class PacketDiscord:
    class Extra:
        class Field:
            MESSAGE = "message"

        @classmethod
        def extra2message(cls, extra):
            return extra.get(cls.Field.MESSAGE)

    @classmethod
    def message2sender_name(cls, message):
        return message.author.name

    @classmethod
    def message2packet(cls, message):
        from khala.singleton.messenger.discord.internal.channel_user_discord import ChannelUserDiscord
        from khala.singleton.messenger.discord.internal.chatroom_discord import ChatroomDiscord

        # extra = {cls.Extra.Field.MESSAGE: message}
        packet = {KhalaPacket.Field.TEXT: message.content,
                  KhalaPacket.Field.CHATROOM: ChatroomDiscord.message2codename(message),
                  KhalaPacket.Field.CHANNEL_USER: ChannelUserDiscord.message2codename(message),
                  KhalaPacket.Field.SENDER_NAME: cls.message2sender_name(message),
                  # KhalaPacket.Field.EXTRA: extra,
                  }
        return packet

    # @classmethod
    # def packet2message(cls, packet):
    #     return cls.Extra.extra2message(KhalaPacket.packet2extra(packet))

    # @classmethod
    # def packet2channel_user_codename(cls, packet):
    #     message = cls.packet2message(packet)
    #
    #     return ChannelUser.channel_suffix2codename(Channel.Codename.DISCORD, message.user.id)

    # @classmethod
    # def packet2username(cls, packet):
    #     message = cls.packet2message(packet)
    #     return message.user.username
