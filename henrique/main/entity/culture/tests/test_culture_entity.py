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
        raise Exception(data_ll)
