import logging
import os
import sys

import yaml
from functools import reduce, lru_cache
from nose.tools import assert_equal

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
# REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*3, FILE_DIR)


class Server:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_server(cls):
        filepath = os.path.join(FILE_DIR, "server.yaml")
        j_server = YAMLTool.filepath2j(filepath, Loader=yaml.SafeLoader)
        return j_server

    @classmethod
    def jpath2ip(cls, jpath):
        logger = HenriqueLogger.func_level2logger(cls.jpath2ip, logging.DEBUG)

        j_server = cls.j_server()
        # logger.debug({"j_server":j_server})

        ip = JsonTool.down(j_server, jpath)
        #logger.debug({"[cls.Constant.ROOT,env,ip]":[cls.Constant.ROOT,env,"ip"]})
        return ip


def main():
    assert_equal(len(sys.argv), 2)
    jpath = sys.argv[1].split(".")

    print(Server.jpath2ip(jpath))


if __name__ == "__main__":
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    main()
