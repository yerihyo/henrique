import logging
import os

import yaml
from functools import reduce, lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
# REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*3, FILE_DIR)


class HenriqueServer:
    class Constant:
        ROOT = "henrique"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_server(cls):
        filepath = os.path.join(FILE_DIR, "server.yaml")
        j_server = YAMLTool.filepath2j(filepath, Loader=yaml.SafeLoader)
        return j_server

    @classmethod
    def env2ip(cls, env):
        logger = HenriqueLogger.func_level2logger(cls.env2ip, logging.DEBUG)

        j_server = cls.j_server()
        # logger.debug({"j_server":j_server})

        ip = JsonTool.down(j_server, [cls.Constant.ROOT,env,"ip"])
        #logger.debug({"[cls.Constant.ROOT,env,ip]":[cls.Constant.ROOT,env,"ip"]})
        return ip

def main():
    env = HenriqueEnv.env()
    print(HenriqueServer.env2ip(env))

if __name__ == "__main__":
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    main()
