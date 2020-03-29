from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from khalalib.packet.packet import KhalaPacket


class TestPortSkill(TestCase):
    def test_01(self):

        packet = {KhalaPacket.Field.TEXT:"?port 리스본",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = PortSkill.packet2response(packet)
        ref = '[리스본]'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
