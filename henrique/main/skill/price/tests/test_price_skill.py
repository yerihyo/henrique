from pprint import pprint
from unittest import TestCase

from henrique.main.skill.price.price_skill import PriceSkill
from khalalib.packet.packet import KhalaPacket


class TestPriceSkill(TestCase):
    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?price 리스본 육두구",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = PriceSkill.packet2response(packet)
        ref = """[리스본] 시세
- 육두구 93 ⇗"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT:"?price 리스본 세비야 육두구 메이스",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = PriceSkill.packet2response(packet)
        ref = """[육두구] 시세
세비야 101 ⇗
리스본 93 ⇗

[메이스] 시세
세비야 101 ⇗
리스본 86 ⇗"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_03(self):
        packet = {KhalaPacket.Field.TEXT: "?price 육메 이베",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = PriceSkill.packet2response(packet)
        ref = """[육두구] 시세
바르셀로나 128 ⇓
발렌시아 126 ⇗
히혼 119 ⇓
팔마 105 ⇓
빌바오 103 ⇗
세비야 101 ⇗
말라가 98 ⇗
사그레스 95 ⇗
리스본 93 ⇗
세우타 84 ⇗
파루 84 ⇓
라스팔마스 82 ⇓
마데이라 74 ⇗
비아나두카스텔루 63 ⇗
몽펠리에 63 ⇗
카사블랑카 62 ⇗
포르투 52 ⇗

[메이스] 시세
파루 116 ⇓
팔마 107 ⇗
빌바오 107 ⇓
세비야 101 ⇗
카사블랑카 94 ⇓
히혼 89 ⇓
몽펠리에 89 ⇓
리스본 86 ⇗
마데이라 80 ⇓
사그레스 77 ⇓
말라가 71 ⇗
세우타 71 ⇓
발렌시아 62 ⇓
라스팔마스 54 ⇗
바르셀로나 53 ⇑
비아나두카스텔루 53 ⇗
포르투 40 ⇓"""

        pprint({"hyp": hyp})
        self.assertEqual(hyp, ref)
