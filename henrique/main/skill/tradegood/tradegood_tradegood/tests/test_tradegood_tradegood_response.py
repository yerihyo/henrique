import logging
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.tradegood.tradegood_tradegood.tradegood_tradegood_response import TradegoodTradegoodResponse


class TestTradegoodTradegoodResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(TradegoodTradegoodResponse.codename_lang2text("Wheat", "ko"))
        ref = """[교역품] 밀
- 종류: [☆1] 식료품
- 판매항: 타코마, 샌프란시스코, 오데사, 잔지바르, 시라쿠사, 코친, 낭트, 케이프타운, 마사와, 세바스토폴, 앤트워프, 튀니스, 코토르, 시에라리온, 아조레스, 파마구스타, 사그레스, 트리폴리, 세비야, 알렉산드리아, 포르투, 카파, 제다, 브레멘, 뤼베크, 소팔라, 발렌시아, 라구사"""

        # pprint(hyp)
        self.assertEqual(hyp, ref)
