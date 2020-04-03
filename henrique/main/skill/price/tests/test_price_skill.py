from pprint import pprint
from unittest import TestCase

from henrique.main.skill.price.price_skill import PriceSkill
from khalalib.packet.packet import KhalaPacket

NORM = PriceSkill.blocks2norm_for_unittest
class TestPriceSkill(TestCase):
    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?price 리스본 육두구",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = NORM(PriceSkill.packet2rowsblocks(packet))
        ref = [('[리스본] 시세', {'육두구'})]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT:"?price 리스본 세비야 육두구 메이스",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = NORM(PriceSkill.packet2rowsblocks(packet))
        ref = [('[육두구] 시세', {'세비야', '리스본'}),
               ('[메이스] 시세', {'세비야', '리스본'}),
               ]

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_03(self):
        packet = {KhalaPacket.Field.TEXT: "?price 육메 이베",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = NORM(PriceSkill.packet2rowsblocks(packet))
        ref = [('[육두구] 시세',
                {'바르셀로나', '발렌시아', "히혼", "팔마", "빌바오", "세비야", "말라가", "사그레스", "리스본", "세우타", "파루", "라스팔마스", "마데이라",
                 "비아나두카스텔루", "몽펠리에", "카사블랑카", "포르투", }),
               ('[메이스] 시세',
                {'바르셀로나', '발렌시아', "히혼", "팔마", "빌바오", "세비야", "말라가", "사그레스", "리스본", "세우타", "파루", "라스팔마스", "마데이라",
                 "비아나두카스텔루", "몽펠리에", "카사블랑카", "포르투", }),
               ]

        # pprint({"hyp": hyp})
        self.assertEqual(hyp, ref)
