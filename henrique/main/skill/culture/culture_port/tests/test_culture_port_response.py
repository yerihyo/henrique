import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.culture.culture_port.culture_port_response import CulturePortResponse
from henrique.main.skill.henrique_skill import Rowsblock


class TestCulturePortResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(CulturePortResponse.codename_lang2text("Lisbon", "ko"))
        ref = "[리스본] 문화권 - 이베리아"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
