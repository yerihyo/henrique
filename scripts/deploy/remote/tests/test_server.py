import logging
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from scripts.deploy.remote.server import Server


class TestServer(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)
        ip = Server.jpath2ip(["henrique","prod","ip"])

        logger.debug({"ip": ip})
        self.assertNotEqual(ip, "localhost")
