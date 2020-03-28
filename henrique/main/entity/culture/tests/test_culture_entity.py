import logging
from unittest import TestCase

from henrique.main.entity.culture.culture_entity import CultureGooglesheets
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestCultureGooglesheets(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        data_ll = CultureGooglesheets.sheetname2data_ll("names.ko")
        self.assertTrue(data_ll)
        self.assertEqual(len(data_ll[0]), 3)
        self.assertEqual(data_ll[1][0],"Northern Europe")
