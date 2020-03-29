import logging
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_culture.port_culture_response import PortCultureResponse


class TestPortCultureResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = HenriqueKhala.response2norm(PortCultureResponse.codename_lang2response("Iberia", "ko"))
        ref = "[이베리아] 항구 - 리스본, 세비야"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
