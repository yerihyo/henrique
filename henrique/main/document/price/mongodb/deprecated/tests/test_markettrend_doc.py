import logging
from unittest import TestCase

import pytest

from foxylib.tools.collections.collections_tool import l_singleton2obj
from henrique.main.document.price.mongodb.deprecated.markettrend_doc import MarkettrendDoc
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc, MarketpriceDict
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestMarkettrendDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    @pytest.mark.skip(reason="not using MarkettrendDoc to read marketprice anymore")
    def test_01(self):
        price_list = MarkettrendDoc.ports_tradegoods2price_list_latest(["Lisbon"], ["Nutmeg"])
        price = l_singleton2obj(price_list)

        self.assertEqual(MarketpriceDoc.price2port(price), "Lisbon")
        self.assertEqual(MarketpriceDoc.price2tradegood(price), "Nutmeg")
        self.assertEqual(MarketpriceDoc.Field.set(), set(price.keys()))
