import logging
from unittest import TestCase

from foxylib.tools.collections.collections_tool import l_singleton2obj
from henrique.main.entity.price.mongodb.markettrend_doc import MarkettrendDoc
from henrique.main.entity.price.marketprice import Marketprice, MarketpriceDict
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestMarkettrendDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        price_list = MarkettrendDoc.ports_tradegoods2price_list_latest(["Lisbon"], ["Nutmeg"])
        price = l_singleton2obj(price_list)

        self.assertEqual(Marketprice.price2port(price), "Lisbon")
        self.assertEqual(Marketprice.price2tradegood(price), "Nutmeg")
        self.assertEqual(Marketprice.Field.set(), set(price.keys()))
