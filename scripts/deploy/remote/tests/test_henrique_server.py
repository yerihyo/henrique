import logging
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from scripts.deploy.remote.henrique_server import HenriqueServer


class TestHenriqueServer(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)
        ip = HenriqueServer.env2ip("prod")

        logger.debug({"ip":ip})
        self.assertNotEqual(ip, "localhost")
