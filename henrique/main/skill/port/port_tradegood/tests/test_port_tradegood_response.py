import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_tradegood.port_tradegood_response import PortTradegoodResponse


class TestPortTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = HenriqueKhala.response2norm(PortTradegoodResponse.tradegood_lang2response("Emerald", "ko"))
        ref = "[에메랄드] 매각처 - 툼베스, 잔지바르, 코친, 디우, 모잠비크, 타마타브, 카라카스"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
