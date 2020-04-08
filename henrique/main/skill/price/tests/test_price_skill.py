import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill import PriceSkill, PriceSkillClique
from khalalib.packet.packet import KhalaPacket

NORM = PriceSkill.blocks2norm_for_unittest


class TestPriceSkillClique(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        entities_list = [[{'span': (6, 10), 'text': '이베리아', 'value': 'Iberia', 'type': 'culture'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Las Palmas',
                         'Faro',
                         'Casablanca',
                         'Gijon',
                         'Palma',
                         'Madeira',
                         'Vianna do Castelo',
                         'Lisbon',
                         'Sagres',
                         'Bilbao',
                         'Seville',
                         'Barcelona',
                         'Porto',
                         'Malaga',
                         'Ceuta',
                         'Montpellier',
                         'Valencia'],
               'tradegoods': ['Nutmeg']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_03(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.text_entities_list2entities_spans_clique("?price 리스본 육두구", entities_list)
        ref = [(0, 2)]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_04(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': 'tradegood'}],
                         ]
        hyp = PriceSkillClique.text_entities_list2clique_list("?price 리스본 육두구", entities_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_05(self):
        entities_list = [[{'span': (7, 8), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                          {'span': (8, 9), 'text': '메', 'value': 'Mace', 'type': 'tradegood'}
                          ],
                         [{'span': (16, 17), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_06(self):
        entity_list = [{'span': (0, 1), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                       {'span': (1, 2), 'text': '메', 'value': 'Mace', 'type': 'tradegood'}
                       ]
        hyp = list(PriceSkill.entity_list2group_spans("육메", entity_list))
        ref = [(0, 2)]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_07(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': 'port'}],
                         [{'span': (11, 12), 'text': '육', 'value': 'Nutmeg', 'type': 'tradegood'},
                          {'span': (12, 13), 'text': '메', 'value': 'Mace', 'type': 'tradegood'},
                          ],
                         ]
        hyp = PriceSkillClique.text_entities_list2clique_list("?price 리스본 육메", entities_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

class TestPriceSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?price 리스본 육두구",
                  KhalaPacket.Field.LOCALE: "ko-KR",
                  }

        hyp = NORM(PriceSkill.packet2rowsblocks(packet))
        ref = [('[리스본] 시세', {'육두구'})]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT: "?price 리스본 세비야 육두구 메이스",
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

        pprint({"hyp": hyp})
        self.assertEqual(hyp, ref)



