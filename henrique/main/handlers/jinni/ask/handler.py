from foxylib.tools.string.string_tools import str2split
from khalalib.chat.chat import Chat
from khalalib.packet.packet import KhalaPacket


class Handler:

    @classmethod
    def jinni_uiud2is_matched(cls, jinni_uuid):
        return True

    @classmethod
    def j_packet2action(cls, j_packet):
        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = Chat.chat2text(j_chat)
        l = str2split(text)
        if l.startswith("?항구"):
            return
    @classmethod
    def post(cls, packet):
        j_packet = packet

        jinni_uuid = KhalaPacket.j_packet2jinni_uuid(j_packet)
        if not cls.jinni_uiud2is_matched(jinni_uuid):
            return "Invalid jinni_uuid ({})".format(jinni_uuid), 400

        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = Chat.chat2text(j_chat)





        return "works", 200