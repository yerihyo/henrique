import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.tradegood.tradegood_tradegood.tradegood_tradegood_response import TradegoodTradegoodResponse


class TestTradegoodTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = HenriqueKhala.response2norm(TradegoodTradegoodResponse.codename_lang2response("Wheat", "ko"))
        ref = '[밀]'

        # pprint(hyp)
        self.assertEqual(hyp, ref)
