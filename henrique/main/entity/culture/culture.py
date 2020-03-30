import os
import sys
from itertools import chain
from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, IterTool, luniq
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool

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
    def _dict_codename2culture(cls):
        from henrique.main.entity.culture.googlesheets.culture_googlesheets import CultureGooglesheets
        culture_list = CultureGooglesheets.culture_list_all()
        assert_is_not_none(culture_list)

        h_codename2culture = merge_dicts([{cls.culture2codename(culture): culture}
                                          for culture in culture_list])
        return h_codename2culture

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def list_all(cls):
        return list(cls._dict_codename2culture().values())

    @classmethod
    def culture2codename(cls, culture):
        return culture[cls.Field.CODENAME]

    @classmethod
    def codename2culture(cls, codename):
        return cls._dict_codename2culture().get(codename)

    @classmethod
    def culture_lang2aliases(cls, culture, lang):
        return JsonTool.down(culture, [cls.Field.ALIASES, lang])


    @classmethod
    def culture_langs2aliases(cls, port, langs):
        return luniq(chain(*[cls.culture_lang2aliases(port, lang) for lang in langs]))

    @classmethod
    def culture_lang2name(cls, culture, lang):
        return IterTool.first(cls.culture_lang2aliases(culture, lang))
