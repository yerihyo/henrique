import os
import sys

from foxylib.tools.collections.collections_tool import merge_dicts
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class Culture:
    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"
        PREFERRED_TRADEGOODS = "preferred_tradegoods"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2culture(cls):
        from henrique.main.entity.culture.culture_googlesheets import CultureGooglesheets
        culture_list = CultureGooglesheets.culture_list_all()

        h_codename2culture = merge_dicts([{cls.culture2codename(culture): culture}
                                          for culture in culture_list])
        return h_codename2culture

    @classmethod
    def culture2codename(cls, culture):
        return culture[cls.Field.CODENAME]

    @classmethod
    def codename2culture(cls, codename):
        return cls.dict_codename2culture().get(codename)



