import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_tradegood.port_tradegood_response import PortTradegoodResponse

class TestPortTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = PortTradegoodResponse.codename_lang2json("Emerald", "ko")
        ref = {'tradegood_name': '에메랄드',
               'port_names': ['디우', '모잠비크', '잔지바르', '카라카스', '코친', '타마타브', '툼베스'],
               }

        # pprint(hyp)
        self.assertEqual(hyp, ref)
