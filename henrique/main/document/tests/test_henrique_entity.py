import logging
from pprint import pprint
from unittest import TestCase

from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill_clique import PriceSkillClique


class TestHenriqueEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        text = "?시세 초롱 : 말세80ㅎ; 사사리75ㅎ; 시라130ㅅ;"
        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = HenriqueEntity.text_extractors2entity_list(text, PriceSkillClique.entity_classes(), config=config)
        ref = [{'span': (4, 6),
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

        pprint(hyp)
        self.assertEqual(hyp, ref)
