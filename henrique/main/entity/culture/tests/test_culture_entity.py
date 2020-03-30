import logging
from unittest import TestCase

from future.utils import lmap

from henrique.main.entity.culture.culture import Culture
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestCultureGooglesheets(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        culture_list = Culture.list_all()
        codename_list = lmap(Culture.culture2codename, culture_list)

        self.assertIn("Northern Europe", codename_list)
