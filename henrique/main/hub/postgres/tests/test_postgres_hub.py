import logging
from unittest import TestCase

import pytest

from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.postgres.postgres_hub import PostgresHub


class PostgresHubTest(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers()

    @pytest.mark.skip(reason="postgres test unnecessary")
    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)

        with PostgresHub.cursor() as cursor:
            cursor.execute("""SELECT * from unchartedwatersonline_port""")
            l = cursor.fetchall()

        logger.debug({"l":l})
