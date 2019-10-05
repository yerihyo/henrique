from henrique.main.entity.port.port_entity import PortEntity
from khalalib.chat.chat import Chat
from khalalib.packet.packet import KhalaPacket


class PortAction:
    @classmethod
    def respond(cls, j_packet):
        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = Chat.chat2text(j_chat)
        
        port_list = PortEntity.str2entity_list(text)

class PortResponse:
    @classmethod
    def port2response(cls, port):
        pass


class CultureResponse:
    @classmethod
    def culture2response(cls, culture):
        pass


class TradegoodResponse:
    @classmethod
    def tradegood2response(cls, tradegood):
        pass
