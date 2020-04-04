import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.henrique_skill import Rowsblock
from henrique.main.skill.tradegood.tradegood_port.tradegood_port_response import TradegoodPortResponse


class TestTradegoodPortResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(TradegoodPortResponse.codename_lang2text("Lisbon", "ko"))
        ref = """[리스본] 상품
- 햄
- 아몬드유
- 닭
- 서양 서적
- 브랜디
- 동광석
- 아몬드
- 도자기
- 단검
- 포탄"""

        pprint(hyp)
        self.assertEqual(hyp, ref)
