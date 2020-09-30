import logging
from pprint import pprint
from unittest import TestCase

from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.document.price.trend.trend_entity import TrendEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestTrendEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = TrendEntity.text2entity_list("120ㅅ", config=config)
        ref = [{'span': (3, 4), 'text': 'ㅅ', 'type': TrendEntity.entity_type(), 'value': 'rise'}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_02(self):
        logger = HenriqueLogger.func_level2logger(self.test_02, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = TrendEntity.text2entity_list("상", config=config)
        ref = []

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_03(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = TrendEntity.text2entity_list("95 하", config=config)
        ref = [{'span': (3, 4), 'text': '하', 'type': TrendEntity.entity_type(), 'value': 'down'}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_04(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = TrendEntity.text2entity_list("95 down", config=config)
        ref = [{'span': (3, 7), 'text': 'down', 'type': TrendEntity.entity_type(), 'value': 'down'}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_05(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "en-US"}
        hyp = TrendEntity.text2entity_list("95 down", config=config)
        ref = [{'span': (3, 7), 'text': 'down', 'type': TrendEntity.entity_type(), 'value': 'down'}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_06(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {HenriqueEntity.Config.Field.LOCALE: "en-US"}
        hyp = TrendEntity.text2entity_list("95 하", config=config)
        ref = []

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)


