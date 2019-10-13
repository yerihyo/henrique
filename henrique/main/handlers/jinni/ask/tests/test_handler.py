from unittest import TestCase

from henrique.main.action.port.port_action import PortAction
from henrique.main.action.tradegood.tradegood_action import TradegoodAction
from henrique.main.handlers.jinni.ask.handler import Handler
from henrique.main.hub.logger.logger import HenriqueLogger
from khalalib.chat.chat import KhalaChat
from khalalib.packet.packet import KhalaPacket


class TestHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers()

    def test_01(self):
        j_chat = KhalaChat.Builder.text2h("?항구 리스본")
        j_packet = KhalaPacket.j_chat2j_packet(j_chat)

        hyp = Handler.j_packet2action(j_packet)
        ref = PortAction
        self.assertEqual(hyp, ref)

    def test_02(self):
        j_chat = KhalaChat.Builder.text2h("?port 리스본")
        j_packet = KhalaPacket.j_chat2j_packet(j_chat)

        hyp = Handler.j_packet2action(j_packet)
        ref = PortAction
        self.assertEqual(hyp, ref)


    def test_03(self):
        j_chat = KhalaChat.Builder.text2h("?ㄱㅇㅍ 리스본")
        j_packet = KhalaPacket.j_chat2j_packet(j_chat)

        hyp = Handler.j_packet2action(j_packet)
        ref = TradegoodAction
        self.assertEqual(hyp, ref)