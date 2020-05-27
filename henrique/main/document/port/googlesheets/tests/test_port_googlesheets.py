import logging
from unittest import TestCase

import pytest

from henrique.main.document.port.googlesheets.port_googlesheets import PortGooglesheets
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestPortGooglesheets(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    @pytest.mark.skip(reason="too long")
    def test_01(self):
        hyp = PortGooglesheets.dict_sheetname2data_ll()

        # pprint(hyp)
        # self.assertEqual(hyp, ref)
