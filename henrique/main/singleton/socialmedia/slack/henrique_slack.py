import logging

from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class HenriqueSlackbot:
    @classmethod
    def xoxb_token(cls):
        logger = HenriqueLogger.func_level2logger(cls.xoxb_token, logging.DEBUG)

        key = "SLACK_HENRIQUE_BOT_USER_OAUTH_ACCESS_TOKEN"
        token = HenriqueEnv.key2value(key)
        logger.debug({"key":key,
                      "bool(token)": bool(token),
                      "token is None": token is None,
                      })
        return token
