import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.skill.tradegood.tradegood_port.tradegood_port_response import TradegoodPortResponse


class TestTradegoodPortResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(TradegoodPortResponse.codename_lang2text("Lisbon", "ko"))
        ref = """[리스본] 상품
- 아몬드
- 아몬드유
- 브랜디
- 포탄
- 도자기
- 닭
- 동광석
- 햄
- 단검
- 서양 서적"""

        # pprint(hyp)
        self.assertEqual(hyp, ref)
