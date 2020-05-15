import logging
import os

from functools import lru_cache, reduce

from foxylib.tools.file.file_tool import FileTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*4, FILE_DIR)


class HenriqueUwsgi:
    class Mode:
        class Value:
            STANDALONE = "standalone"
            NGINX = "nginx"

            @classmethod
            def list(cls):
                return [cls.STANDALONE, cls.NGINX]


    @classmethod
    def env2mode(cls, env):
        h = {HenriqueEnv.Value.LOCAL: cls.Mode.Value.STANDALONE,
             HenriqueEnv.Value.DEV: cls.Mode.Value.NGINX,
             HenriqueEnv.Value.PROD: cls.Mode.Value.NGINX,
             }
        return h[env]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def template(cls):
        filepath = os.path.join(FILE_DIR, "henrique.uwsgi.ini.tmplt")
        utf8 = FileTool.filepath2utf8(filepath)
        template = Jinja2Renderer.env_text2template(None, utf8)
        return template

    @classmethod
    def mode2compile(cls, mode):
        data = {"mode": mode,
                }

        filepath = os.path.join(FILE_DIR, "ini", "henrique.uwsgi.{}.ini".format(mode))
        utf8 = Jinja2Renderer.template2text(cls.template(), data=data)
        FileTool.utf82file(utf8, filepath)

    @classmethod
    def compile_all(cls):
        for mode in cls.Mode.Value.list():
            cls.mode2compile(mode)


def main():
    HenriqueUwsgi.compile_all()


if __name__== "__main__":
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    main()

