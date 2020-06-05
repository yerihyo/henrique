import logging
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.tradegood.tradegood_culture.tradegood_culture_response import TradegoodCultureResponse


class TestTradegoodCultureResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(TradegoodCultureResponse.codename_lang2text("Iberia", "ko"))
        ref = """[교역품] 이베리아 문화권 우대품
- 타네가시마 총
- 대만 목각
- 유자
- 일본서적
- 사마 은
- 스타아니스
- 호필
- 두반장
- 가는 끈
- 산초
- 진달래
- 진과스 금
- 청룡도
- 사슴 가죽
- 한지
- 자근
- 사다장"""
        # pprint(hyp)
        self.assertEqual(hyp, ref)
