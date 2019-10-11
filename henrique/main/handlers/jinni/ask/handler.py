from foxylib.tools.string.string_tools import str2split
from henrique.main.action.port.port_action import PortAction
from khalalib.chat.chat import KhalaChat
from khalalib.packet.packet import KhalaPacket


class Handler:

    @classmethod
    def jinni_uiud2is_matched(cls, jinni_uuid):
        return True

    @classmethod
    def j_packet2action(cls, j_packet):
        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text_body = KhalaChat.j_chat2text_body(j_chat)

        l = str2split(text_body)
        if not l: return None

        if l[0] == "항구": return PortAction

    @classmethod
    def post(cls, packet):
        j_packet = packet

        jinni_uuid = KhalaPacket.j_packet2jinni_uuid(j_packet)
        if not cls.jinni_uiud2is_matched(jinni_uuid):
            return "Invalid jinni_uuid ({})".format(jinni_uuid), 400

        action = cls.j_packet2action(j_packet)
        action.respond(j_packet)






        return "works", 200