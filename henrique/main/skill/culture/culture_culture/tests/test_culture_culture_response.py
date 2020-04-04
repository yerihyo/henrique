import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.culture.culture_culture.culture_culture_response import CultureCultureResponse
from henrique.main.skill.henrique_skill import Rowsblock


class TestCultureCultureResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(CultureCultureResponse.codename_lang2text("Iberia", "ko"))
        ref = '[이베리아]'

        # pprint(hyp)
        self.assertEqual(hyp, ref)
