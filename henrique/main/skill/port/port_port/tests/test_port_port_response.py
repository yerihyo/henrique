import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.skill.port.port_port.port_port_response import PortPortResponse


class TestPortPortResponse(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = Rowsblock.text2norm(PortPortResponse.codename_lang2text("Lisbon", "ko"))
        ref = """[리스본]
- 문화권: 이베리아
- 내성: 식료품, 가축, 조미료, 주류, 기호품, 광석, 무기류, 공예품, 총포류"""

        # pprint(hyp)
        self.assertEqual(hyp, ref)
