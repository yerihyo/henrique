import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_culture.port_culture_response import PortCultureResponse


NORM = PortCultureResponse.data2norm_unittest

class TestPortCultureResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = NORM(PortCultureResponse.codename_lang2json("Northern Europe", "ko"))
        ref = {'culture_name': '북유럽',
               'port_names': {'스톡홀름', '오슬로', '뤼베크', '리가', '코펜하겐', '단치히', '베르겐', '코콜라', '비스뷔'},
               }

        # pprint(hyp)
        self.assertEqual(hyp, ref)
