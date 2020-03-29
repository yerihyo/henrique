import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_culture.port_culture_response import PortCultureResponse


class TestPortCultureResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = HenriqueKhala.response2norm(PortCultureResponse.codename_lang2response("Northern Europe", "ko"))
        ref = "[북유럽] 항구 - 베르겐, 단치히, 스톡홀름, 코콜라, 코펜하겐, 오슬로, 리가, 뤼베크, 비스뷔"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
