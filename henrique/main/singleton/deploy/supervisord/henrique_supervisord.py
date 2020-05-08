import logging
import os
from functools import lru_cache, reduce

from foxylib.tools.file.file_tool import FileTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.jinja2.jinja2_tool import Jinja2Tool, Jinja2Renderer
from henrique.main.singleton.deploy.nginx.henrique_nginx import HenriqueNginx
from henrique.main.singleton.deploy.uwsgi.henrique_uwsgi import HenriqueUwsgi
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*5, FILE_DIR)


class HenriqueSupervisord:
    @classmethod
    def env2domain_name(cls, env):
        h = {HenriqueEnv.Value.LOCAL: "localhost",
             HenriqueEnv.Value.DEV: "dev.henrique.way2gosu.com",
             HenriqueEnv.Value.PROD: "henrique.way2gosu.com",
             }
        return h[env]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def template(cls):
        filepath = os.path.join(FILE_DIR, "henrique.supervisord.conf.tmplt")
        utf8 = FileTool.filepath2utf8(filepath)
        template = Jinja2Renderer.env_text2template(None, utf8)
        return template

    @classmethod
    def env2compile(cls, env):
        logger = HenriqueLogger.func_level2logger(cls.env2compile, logging.DEBUG)
        logger.debug({"env":env})

        uwsgi_mode = HenriqueUwsgi.env2mode(env)

        nginx_mode = HenriqueNginx.env2mode(env)
        uid = HenriqueNginx.Mode.mode2user(nginx_mode)
        gid = HenriqueNginx.Mode.mode2group(nginx_mode)

        data = {"env": env,
                "uid": uid,
                "gid": gid,
                "uwsgi_mode":uwsgi_mode,
                }

        filepath = os.path.join(FILE_DIR, "conf", "henrique.supervisord.{}.conf".format(env))
        utf8 = Jinja2Renderer.template2text(cls.template(), data=data)
        FileTool.utf82file(utf8, filepath)

        logger.debug({"filepath": filepath,
                      "data":data,
                      })

    @classmethod
    def compile_all(cls):
        for env in HenriqueEnv.Value.list():
            cls.env2compile(env)


def main():
    HenriqueSupervisord.compile_all()

if __name__== "__main__":
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    main()

