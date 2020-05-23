import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.price.rate.rate_entity import RateEntity
from henrique.main.document.price.trend.trend_entity import TrendEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill import PriceSkill
from henrique.main.skill.price.price_skill_clique import PriceSkillClique

NORM_LIST = PriceSkill.blocks2norm_list_for_unittest
NORM_SET = PriceSkill.blocks2norm_set_for_unittest


class TestPriceSkillClique(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        entities_list = [[{'span': (6, 10), 'text': '이베리아', 'value': 'Iberia', 'type': CultureEntity.entity_type()}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()}],
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
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()}],
                         ]
        hyp = PriceSkillClique.text_entities_list2indexes_list("?price 리스본 육두구", entities_list)
        ref = [[0,1]]

        pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_04(self):
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()},
                       {'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()},
                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list("?price 리스본 육두구", entity_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_05(self):
        entities_list = [[{'span': (7, 8), 'text': '육', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()},
                          {'span': (8, 9), 'text': '메', 'value': 'Mace', 'type': TradegoodEntity.entity_type()}
                          ],
                         [{'span': (16, 17), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_06(self):
        entity_list = [{'span': (0, 1), 'text': '육', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()},
                       {'span': (1, 2), 'text': '메', 'value': 'Mace', 'type': TradegoodEntity.entity_type()}
                       ]
        hyp = list(PriceSkillClique.entity_list2group_spans("육메", entity_list))
        ref = [(0, 2)]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_07(self):
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()},
                       {'span': (11, 12), 'text': '육', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()},
                       {'span': (12, 13), 'text': '메', 'value': 'Mace', 'type': TradegoodEntity.entity_type()},

                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list("?price 리스본 육메", entity_list)
        ref = [{'ports': ['Lisbon'], 'tradegoods': ['Nutmeg', 'Mace']}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_11(self):
        entities_list = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()}],
                         [{'span': (11, 14), 'text': '육두구', 'value': 'Nutmeg', 'type': TradegoodEntity.entity_type()}],
                         [{'span': (15, 18), 'text': '120', 'value': 120, 'type': RateEntity.entity_type()}],
                         [{'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': TrendEntity.entity_type()}],
                         ]
        hyp = PriceSkillClique.entities_list2clique(entities_list)
        ref = {'ports': ['Lisbon'], 'rate': 120, 'tradegoods': ['Nutmeg'], 'trend': 'rise'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_12(self):
        text = "?price 리스본 사탕무 120 ㅅ"
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()},
                       {'span': (11, 14), 'text': '사탕무', 'value': 'Sugar Beet', 'type': TradegoodEntity.entity_type()},
                       {'span': (15, 18), 'text': '120', 'value': 120, 'type': RateEntity.entity_type()},
                       {'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': TrendEntity.entity_type()},
                       ]
        hyp = PriceSkillClique.entity_list2entities_list_grouped(text, entity_list)
        ref = [[{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()}],
               [{'span': (11, 14), 'text': '사탕무', 'value': 'Sugar Beet', 'type': TradegoodEntity.entity_type()}],
               [{'span': (15, 18), 'text': '120', 'value': 120, 'type': RateEntity.entity_type()}],
               [{'span': (19, 20), 'text': 'ㅅ', 'value': "rise", 'type': TrendEntity.entity_type()}],
               ]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_13(self):
        text = "?price 리스본 밀가루 120ㅅ"
        entity_list = [{'span': (7, 10), 'text': '리스본', 'value': 'Lisbon', 'type': PortEntity.entity_type()},
                       {'span': (11, 14), 'text': '사탕무', 'value': 'Sugar Beet', 'type': TradegoodEntity.entity_type()},
                       {'span': (15, 18), 'text': '120', 'value': 120, 'type': RateEntity.entity_type()},
                       {'span': (18, 19), 'text': 'ㅅ', 'value': "rise", 'type': TrendEntity.entity_type()},
                       ]
        hyp = PriceSkillClique.text_entity_list2clique_list(text, entity_list)
        ref = [{'ports': ['Lisbon'], 'rate': 120, 'tradegoods': ['Sugar Beet'], 'trend': 'rise'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_14(self):
        text = "?시세 초롱 : 말세80ㅎ; 사사리75ㅎ; 시라130ㅅ;"
        entity_list = [{'span': (4, 6),
                        'text': '초롱',
                        'type': 'henrique.main.document.tradegood.tradegood_entity.TradegoodEntity',
                        'value': 'Paper Lantern'},
                       {'span': (9, 11),
                        'text': '말세',
                        'type': 'henrique.main.document.port.port_entity.PortEntity',
                        'value': 'Marseilles'},
                       {'span': (11, 13),
                        'text': '80',
                        'type': 'henrique.main.document.price.rate.rate_entity.RateEntity',
                        'value': 80},
                       {'span': (13, 14),
                        'text': 'ㅎ',
                        'type': 'henrique.main.document.price.trend.trend_entity.TrendEntity',
                        'value': 'down'},
                       {'span': (16, 19),
                        'text': '사사리',
                        'type': 'henrique.main.document.port.port_entity.PortEntity',
                        'value': 'Sassari'},
                       {'span': (19, 21),
                        'text': '75',
                        'type': 'henrique.main.document.price.rate.rate_entity.RateEntity',
                        'value': 75},
                       {'span': (21, 22),
                        'text': 'ㅎ',
                        'type': 'henrique.main.document.price.trend.trend_entity.TrendEntity',
                        'value': 'down'},
                       {'span': (24, 26),
                        'text': '시라',
                        'type': 'henrique.main.document.port.port_entity.PortEntity',
                        'value': 'Syracuse'},
                       {'span': (26, 29),
                        'text': '130',
                        'type': 'henrique.main.document.price.rate.rate_entity.RateEntity',
                        'value': 130},
                       {'span': (29, 30),
                        'text': 'ㅅ',
                        'type': 'henrique.main.document.price.trend.trend_entity.TrendEntity',
                        'value': 'rise'}]

        hyp = PriceSkillClique.text_entity_list2clique_list(text, entity_list)
        ref = [{'ports': ['Marseilles'],
                'rate': 80,
                'tradegoods': ['Paper Lantern'],
                'trend': 'down'},
               {'ports': ['Sassari'],
                'rate': 75,
                'tradegoods': ['Paper Lantern'],
                'trend': 'down'},
               {'ports': ['Syracuse'],
                'rate': 130,
                'tradegoods': ['Paper Lantern'],
                'trend': 'rise'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_15(self):
        text = "?시세 사탕무 : 말세80ㅎ; 사사리75ㅎ; 시라130ㅅ;"
        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        entity_list = Entity.text_extractors2entity_list(text, PriceSkillClique.entity_classes(), config=config)
        hyp = PriceSkillClique.text_entity_list2clique_list(text, entity_list)
        ref = [{'ports': ['Marseilles'],
                'rate': 80,
                'tradegoods': ['Sugar Beet'],
                'trend': 'down'},
               {'ports': ['Sassari'],
                'rate': 75,
                'tradegoods': ['Sugar Beet'],
                'trend': 'down'},
               {'ports': ['Syracuse'],
                'rate': 130,
                'tradegoods': ['Sugar Beet'],
                'trend': 'rise'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)


