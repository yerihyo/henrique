from pprint import pprint
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

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT:"?port 이베리아",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = PortSkill.packet2response(packet)
        ref = '[이베리아] 항구 - 라스팔마스, 카사블랑카, 비아나두카스텔루, 파루, 마데이라, 팔마, 히혼, 리스본, 세비야, 빌바오, 사그레스, 바르셀로나, 세우타, 포르투, 말라가, 몽펠리에, 발렌시아'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
