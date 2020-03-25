from unittest import TestCase

import pytest

from henrique.main.handlers.khala.packet_handler import PacketHandler
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_skill import PortSkill
from khalalib.packet.packet import KhalaPacket, KhalaPacket


class TestHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers()

    @pytest.mark.skip(reason="handler not yet working")
    def test_01(self):
        packet = {
            KhalaPacket.Field.TEXT: "?항구 리스본",
        }

        hyp = PacketHandler.post(packet)
        ref = PortSkill
        self.assertEqual(hyp, ref)

    @pytest.mark.skip(reason="handler not yet working")
    def test_02(self):
        packet = {
            KhalaPacket.Field.TEXT: "?port 리스본",
        }

        hyp = PacketHandler.post(packet)
        ref = PortSkill
        self.assertEqual(hyp, ref)

    @pytest.mark.skip(reason="handler not yet working")
    def test_03(self):
        packet = {
            KhalaPacket.Field.TEXT: "?ㄱㅇㅍ 리스본",
        }

        hyp = PacketHandler.post(packet)
        ref = TradegoodAction
        self.assertEqual(hyp, ref)