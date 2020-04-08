import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.henrique_entity import Entity
from henrique.main.document.price.rate.rate_entity import RateEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestRateEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)

        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = RateEntity.text2entity_list("120ㅅ", config=config)
        ref = [{'span': (0, 3), 'text': '120', 'type': 'rate', 'value': 120}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_02(self):
        logger = HenriqueLogger.func_level2logger(self.test_02, logging.DEBUG)

        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = RateEntity.text2entity_list("200", config=config)
        ref = [{'span': (0, 3), 'text': '200', 'type': 'rate', 'value': 200}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_03(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {Entity.Config.Field.LOCALE: "en-US"}
        hyp = RateEntity.text2entity_list("95하", config=config)
        ref = []

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)

    def test_04(self):
        logger = HenriqueLogger.func_level2logger(self.test_03, logging.DEBUG)

        config = {Entity.Config.Field.LOCALE: "ko-KR"}
        hyp = RateEntity.text2entity_list("95down", config=config)
        ref = [{'span': (0, 2), 'text': '95', 'type': 'rate', 'value': 95}]

        # pprint({"hyp":hyp})

        self.assertEqual(hyp, ref)




