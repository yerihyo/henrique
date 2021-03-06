import logging
from unittest import TestCase

import pytest

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres


class HenriquePostgresTest(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    @pytest.mark.skip(reason="postgres test unnecessary")
    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)

        with HenriquePostgres.cursor() as cursor:
            cursor.execute("""SELECT * from unchartedwatersonline_port""")
            l = cursor.fetchall()

        logger.debug({"l":l})
