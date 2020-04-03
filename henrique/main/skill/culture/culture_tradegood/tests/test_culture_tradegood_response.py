import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.culture.culture_tradegood.culture_tradegood_response import CultureTradegoodResponse


class TestCultureTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = HenriqueKhala.response2norm(CultureTradegoodResponse.codename_lang2text("Tanegashima Rifle", "ko"))
        ref = """[타네가시마 총] 우대 문화권
- 이베리아"""

        # pprint(hyp)
        self.assertEqual(hyp, ref)
