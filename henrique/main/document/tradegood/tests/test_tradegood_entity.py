import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.henrique_entity import Entity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestTradegoodEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = TradegoodEntity.text2entity_list("육두구 메이스 크로브", config=config)

        ref = [{'span': (0, 3), 'text': '육두구', 'type': TradegoodEntity.entity_type(), 'value': 'Nutmeg'},
               {'span': (4, 7), 'text': '메이스', 'type': TradegoodEntity.entity_type(), 'value': 'Mace'},
               {'span': (8, 11), 'text': '크로브', 'type': TradegoodEntity.entity_type(), 'value': 'Cloves'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = TradegoodEntity.text2entity_list("육메", config=config)

        ref = [{'span': (0, 1), 'text': '육', 'type': TradegoodEntity.entity_type(), 'value': 'Nutmeg'},
               {'span': (1, 2), 'text': '메', 'type': TradegoodEntity.entity_type(), 'value': 'Mace'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_03(self):
        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = TradegoodEntity.text2entity_list("육메크", config=config)

        ref = [{'span': (0, 1), 'text': '육', 'type': TradegoodEntity.entity_type(), 'value': 'Nutmeg'},
               {'span': (1, 2), 'text': '메', 'type': TradegoodEntity.entity_type(), 'value': 'Mace'},
               {'span': (2, 3), 'text': '크', 'type': TradegoodEntity.entity_type(), 'value': 'Cloves'},
               ]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_04(self):
        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = TradegoodEntity.text2entity_list("육메클", config=config)

        ref = [{'span': (0, 1), 'text': '육', 'type': TradegoodEntity.entity_type(), 'value': 'Nutmeg'},
               {'span': (1, 2), 'text': '메', 'type': TradegoodEntity.entity_type(), 'value': 'Mace'},
               {'span': (2, 3), 'text': '클', 'type': TradegoodEntity.entity_type(), 'value': 'Cloves'},
               ]

        # pprint(hyp)
        self.assertEqual(hyp, ref)
