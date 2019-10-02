from khalalib.chat.chat import Chat
from khalalib.packet.packet import KhalaPacket


class Handler:

    @classmethod
    def jinni_uiud2is_matched(cls, jinni_uuid):
        return True

    @classmethod
    def post(cls, packet):
        j_packet = packet

        jinni_uuid = KhalaPacket.j_packet2jinni_uuid(j_packet)
        if not cls.jinni_uiud2is_matched(jinni_uuid):
            return "Invalid jinni_uuid ({})".format(jinni_uuid), 400

        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = Chat.chat2text(j_chat)




        return "works", 200