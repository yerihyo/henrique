import logging
import os
from functools import lru_cache, reduce

from foxylib.tools.file.file_tool import FileTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.jinja2.jinja2_tool import Jinja2Tool, Jinja2Renderer
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
NGINX_DIR = os.path.dirname(FILE_DIR)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*4, FILE_DIR)


class HenriqueNginx:
    class Constant:
        FILEPATH_SSL_CERTI = os.path.join(REPO_DIR,"/env/ssl/ssl_certificate.pem")
        FILEPATH_SSL_PRIVATE_KEY = os.path.join(REPO_DIR,"/env/ssl/ssl_private_key.pem")

    class Mode:
        class Value:
            STANDALONE = "standalone"
            DOCKER = "docker"

        @classmethod
        def mode2socket(cls, mode):
            h = {cls.Value.STANDALONE: "{{REPO_DIR}}/scripts/deploy/uwsgi/henrique.uwsgi.sock",
                 cls.Value.DOCKER: "/run/uwsgi.sock",
                 }
            return h[mode]

        @classmethod
        def mode2nginx_dir(cls, mode):
            h = {cls.Value.STANDALONE: "/usr/local/etc/nginx",
                 cls.Value.DOCKER: "/etc/nginx",
                 }
            return h[mode]

        @classmethod
        def mode2user(cls, mode):
            h = {cls.Value.STANDALONE: "moon",
                 cls.Value.DOCKER: "www-data",
                 }
            return h[mode]

        @classmethod
        def mode2group(cls, mode):
            h = {cls.Value.STANDALONE: "staff",
                 cls.Value.DOCKER: "www-data",
                 }
            return h[mode]

        @classmethod
        def mode2user_group(cls, mode):
            return " ".join([cls.mode2user(mode), cls.mode2group(mode)])

    @classmethod
    def env2mode(cls, env):
        h = {HenriqueEnv.Value.LOCAL: cls.Mode.Value.STANDALONE,
             HenriqueEnv.Value.DEV: cls.Mode.Value.DOCKER,
             HenriqueEnv.Value.PROD: cls.Mode.Value.DOCKER,
             }
        return h[env]

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
        filepath = os.path.join(FILE_DIR, "henrique.nginx.conf.tmplt")
        utf8 = FileTool.filepath2utf8(filepath)
        template = Jinja2Renderer.env_text2template(None, utf8)
        return template

    @classmethod
    def env2compile(cls, env):
        domain_name = cls.env2domain_name(env)

        mode = cls.env2mode(env)
        nginx_dir = cls.Mode.mode2nginx_dir(mode)
        socket = cls.Mode.mode2socket(mode)
        user_group = cls.Mode.mode2user_group(mode)

        data = {"DOMAIN_NAME": domain_name,
                "NGINX_DIR": nginx_dir,
                "socket": socket,
                "user_group": user_group,
                "FILEPATH_SSL_CERTI": None,
                "FILEPATH_SSL_PRIVATE_KEY": None,
                }

        filepath = os.path.join(NGINX_DIR, "henrique.nginx.{}.conf".format(env))
        utf8 = Jinja2Renderer.template2text(cls.template(), data=data)
        FileTool.utf82file(utf8, filepath)

    @classmethod
    def compile_all(cls):
        for env in HenriqueEnv.Value.list():
            cls.env2compile(env)


def main():
    HenriqueNginx.compile_all()

if __name__== "__main__":
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    main()

