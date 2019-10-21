import logging
import os
import re
import sys
from functools import lru_cache

from future.utils import lmap, lfilter
from itertools import product

from foxylib.tools.collections.collections_tools import vwrite_no_duplicate_key, merge_dicts, lchain, \
    iter2duplicate_list, iter2singleton
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.env.env_tools import EnvToolkit
from foxylib.tools.function.function_tools import FunctionToolkit
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tools import jdown
from foxylib.tools.json.yaml_tools import YAMLToolkit
from foxylib.tools.regex.regex_tools import RegexToolkit
from foxylib.tools.string.string_tools import str2lower
from henrique.main.hub.entity.entity import Entity
from henrique.main.hub.env.henrique_env import HenriqueEnv
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class ServerDocument:
    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "server.yaml")
        j = YAMLToolkit.filepath2j(filepath)
        return j



WARMER.warmup()


