import logging
from unittest import TestCase

from foxylib.tools.collections.collections_tool import l_singleton2obj
from henrique.main.entity.price.mongodb.markettrend_doc import MarkettrendDoc
from henrique.main.entity.price.price import Price
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestMarkettrendDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        price_dict = MarkettrendDoc.ports_tradegoods2price_dict(["Lisbon"], ["Nutmeg"])

        self.assertEqual(list(price_dict.keys()), [('Lisbon', 'Nutmeg')])
        price = l_singleton2obj(list(price_dict.values()))

        self.assertEqual(Price.Field.set(), set(price.keys()))
