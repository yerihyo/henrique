import logging
import os
from unittest import TestCase

import requests

from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.log.foxylib_logger import FoxylibLogger
from henrique.main.singleton.socialmedia.slack.foxytrixy_server import ErrorsChannel

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TestErrorsChannel(TestCase):
    @classmethod
    def setUpClass(cls):
        FoxylibLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = FoxylibLogger.func_level2logger(self.test_01, logging.DEBUG)

        response1 = ErrorsChannel.post("testing...")
        self.assertEqual(response1.status_code, requests.codes.ok, response1)

        j1 = response1.json()
        # logger.debug({"j1":j1})
        self.assertTrue(j1.get("ok"), response1.content)

        ts = JsonTool.down(j1, ["message","ts"])
        response2 = ErrorsChannel.delete(ts)
        self.assertEqual(response2.status_code, requests.codes.ok, response2)

        j2 = response2.json()
        self.assertTrue(j2.get("ok"), response2.content)

