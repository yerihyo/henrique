from future.utils import lfilter

from henrique.main.concepts.port.port_action import PortAction
from henrique.main.concepts.tradegood.tradegood_action import TradegoodAction
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

        # l = str2split(text_body)
        if not text_body: return None

        action_list = [PortAction, TradegoodAction]

        action_list_matched = lfilter(lambda x:x.text_body2match(text_body), action_list)
        if not action_list_matched: return None
        if len(action_list_matched)>1: return None

        return action_list_matched[0]

    @classmethod
    def post(cls, packet):
        j_packet = packet

        jinni_uuid = KhalaPacket.j_packet2jinni_uuid(j_packet)
        if not cls.jinni_uiud2is_matched(jinni_uuid):
            return "Invalid jinni_uuid ({})".format(jinni_uuid), 400

        action = cls.j_packet2action(j_packet)
        j_response = action.respond(j_packet)
        return j_response, 200