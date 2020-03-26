import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.tradegood_entity.port_tradegood_response import PortTradegoodResponse


class TestPortTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = PortTradegoodResponse.codename_lang2response("Emerald", "ko")
        ref = '[리스본]'

        pprint(hyp)
        self.assertEqual(hyp, ref)
