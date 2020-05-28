# https://pypi.org/project/slackclient/

import logging

import requests
from nose.tools import assert_true

from foxylib.tools.log.foxylib_logger import FoxylibLogger
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.socialmedia.slack.henrique_slack import HenriqueSlackbot


class ErrorsChannel:
    # @classmethod
    # def url(cls):
    #     logger = FoxylibLogger.func_level2logger(cls.url, logging.DEBUG)
    #
    #     url = HenriqueEnv.key2value("SLACK_FOXYTRIXY_ERRORS_URL")
    #     logger.debug({"url": url})
    #     assert_true(url)
    #
    #     return url
    #
    # @classmethod
    # def post_using_url(cls, text):
    #     headers = { 'Content-type': 'application/json'}
    #     j = {"text":text}
    #     response = requests.post(cls.url(), headers=headers, json=j)
    #     return response

    @classmethod
    def channel(cls):
        return "C014DTPM24V"

    @classmethod
    def post(cls, text):
        logger = HenriqueLogger.func_level2logger(cls.post, logging.DEBUG)

        headers = {"Content-type": 'application/json',
                   "Authorization": "Bearer {}".format(HenriqueSlackbot.xoxb_token()),
                   }
        j = {"channel": cls.channel(),
             "text": text,
             }

        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers=headers,
                                 json=j)
        return response

    @classmethod
    def delete(cls, ts):
        logger = HenriqueLogger.func_level2logger(cls.post, logging.DEBUG)

        headers = {"Content-type": 'application/json',
                   "Authorization": "Bearer {}".format(HenriqueSlackbot.xoxb_token()),
                   }
        j = {"channel": cls.channel(),
             "ts": ts,
             }

        response = requests.post("https://slack.com/api/chat.delete",
                                 headers=headers,
                                 json=j)
        return response
