import logging
import os
import re
import sys
from functools import lru_cache

from future.utils import lmap, lfilter
from itertools import product

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, lchain, \
    iter2duplicate_list, iter2singleton
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2lower
from henrique.main.singleton.entity.entity import Entity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class ServerDocument:
    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "server.yaml")
        j = YAMLTool.filepath2j(filepath)
        return j



WARMER.warmup()


