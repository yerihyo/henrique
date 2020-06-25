import logging
from pprint import pprint
from unittest import TestCase

from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.document.tradegoodtype.tradegoodtype_entity import TradegoodtypeEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestTradegoodtypeEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = TradegoodtypeEntity.text2entity_list("식료품 조미", config=config)

        ref = [{'span': (0, 3),
                'text': '식료품',
                'type': 'henrique.main.document.tradegoodtype.tradegoodtype_entity.TradegoodtypeEntity',
                'value': 'Foodstuffs'},
               {'span': (4, 6),
                'text': '조미',
                'type': 'henrique.main.document.tradegoodtype.tradegoodtype_entity.TradegoodtypeEntity',
                'value': 'Seasonings'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

