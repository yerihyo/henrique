class KhalaPacket:
    class Field:
        TEXT = "text"
        # LOCALE = "locale"

        CHATROOM = "chatroom"
        CHANNEL_USER = "channel_user"
        SENDER_NAME = "sender_name"

        # CHANNEL = "channel"
        EXTRA = "extra"


        # SENDER_ID = "sender_id"
        # TYPE = "type"
        # CHATROOM_ID = "chatroom_id"

    @classmethod
    def packet2text(cls, packet):
        return packet[cls.Field.TEXT]

    @classmethod
    def packet2chatroom(cls, packet):
        return packet[cls.Field.CHATROOM]

    @classmethod
    def packet2channel_user(cls, packet):
        return packet[cls.Field.CHANNEL_USER]

    @classmethod
    def packet2sender_name(cls, packet):
        return packet[cls.Field.SENDER_NAME]


    # @classmethod
    # def packet2locale(cls, packet):
    #     from khala.document.chatroom.chatroom import Chatroom
    #
    #     chatroom = cls.packet2chatroom(packet)
    #     return Chatroom.chatroom2locale(chatroom)

    # @classmethod
    # def packet2channel(cls, packet):
    #     return packet[cls.Field.CHANNEL]

    @classmethod
    def packet2extra(cls, packet):
        return packet[cls.Field.EXTRA]

    # @classmethod
    # def packet2channel_user_id(cls, packet):
    #     return packet[cls.Field.CHANNEL_USER_ID]







