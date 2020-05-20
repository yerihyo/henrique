import logging
import os

import connexion
from functools import lru_cache, reduce, wraps

from foxylib.tools.flask.flask_tool import FlaskToolSessionType, FlaskTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.wtforms.wtforms_tool import WTFormsTool
from henrique.front.henrique_front import HenriqueFront
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*3, FILE_DIR)


class HenriqueFlaskConfig:
    class Field:
        SESSION_TYPE = "SESSION_TYPE"
        SECRET_KEY = "SECRET_KEY"
        SECURITY_PASSWORD_SALT = "SECURITY_PASSWORD_SALT"


    @classmethod
    def config(cls):
        config = {cls.Field.SESSION_TYPE: FlaskToolSessionType.V.FILESYSTEM,  # "filesystem",
                  cls.Field.SECRET_KEY: "henrique_secret",
                  cls.Field.SECURITY_PASSWORD_SALT: "henrique_secret second",
                  }
        return config


class HenriqueFlask:
    @classmethod
    def env2port(cls, env):
        env_norm = HenriqueEnv.env2norm(env)

        h = {HenriqueEnv.Value.LOCAL: 14920,
             HenriqueEnv.Value.DEV: 14920,
             HenriqueEnv.Value.STAGING: 14920,
             HenriqueEnv.Value.PROD: 80,
             }
        return h.get(env_norm)

    @classmethod
    def app_context_decorator(cls, func=None):
        def wrapper(f):
            @wraps(f)
            def wrapped(*_, **__):
                with cls.app().app_context():
                    return f(*_, **__)

            return wrapped

        return wrapper(func) if func else wrapper

    @classmethod
    def _load_urls2app(cls, app):
        logger = HenriqueLogger.func_level2logger(cls._load_urls2app, logging.DEBUG)

        from henrique.front.path.view import IndexView
        FlaskTool.add_url2app(app, IndexView.url(), IndexView.get, methods=["GET",])

        # from henrique.front.path.channel.kakaotalk.chatroom.uwo.view import KakaotalkUWOView
        # FlaskTool.add_url2app(app, KakaotalkUWOView.url(), KakaotalkUWOView.get, methods=["GET", ])

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def app(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
        logger = HenriqueLogger.func_level2logger(cls.app, logging.DEBUG)
        logger.debug({"START": "START"})

        # WTForm
        WTFormsTool.json_init()

        # warmup
        from henrique.main.singleton.warmer.henrique_warmer import HenriqueWarmer
        HenriqueWarmer.warmup_all()

        application = connexion.FlaskApp(__name__, )
        # application.add_api('swagger.yaml', resolver=RestyResolver("ariana.main"))
        application.add_api('swagger.yaml')

        app = application.app
        app.static_folder = HenriqueFront.dirpath_static()
        app.config.update(HenriqueFlaskConfig.config())
        logger.debug({"app.secret_key": app.secret_key})

        # from henrique.singleton.auth0.henrique_auth0 import HenriqueAuth0
        # HenriqueAuth0.app2auth0(app)

        cls._load_urls2app(app)
        # raise Exception()

        logger.debug({"END": "END"})
        return app

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def test_client(cls):
        logger = HenriqueLogger.func_level2logger(cls.test_client, logging.DEBUG)
        logger.debug({"START": "START"})
        c = cls.app().test_client()

        logger.debug({"END": "END"})
        return c

app = HenriqueFlask.app()



def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    app.run()


if __name__ == '__main__':
    main()

