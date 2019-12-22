import re
import sys
from functools import lru_cache

from foxylib.tools.collections.collections_tool import lchain
from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2split
from henrique.main.hub.env.henrique_env import HenriqueEnv

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class KhalaAction:
    class Field:
        DEFAULT_ACTION_NAMES = "default_action_names"

    @classmethod
    def j_yaml2p_command(cls, j_yaml):
        h_lang2names = j_yaml.get("default_action_names")

        rstr = RegexTool.rstr_list2or(lchain(*list(h_lang2names.values())))
        return re.compile("{}$".format(rstr), re.I)

    @classmethod
    def pattern_text2match(cls, p, text_body):
        l = str2split(text_body)
        m = p.match(l[0])
        return m

WARMER.warmup()