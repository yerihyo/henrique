import os
import sys
from itertools import chain
from nose.tools import assert_is_not_none

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.collections.collections_tool import merge_dicts, luniq
from functools import lru_cache

from foxylib.tools.collections.groupby_tool import dict_groupby_tree, GroupbyTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class Culture:
    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"
        PREFERS = "prefers"

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
    def culture2prefers(cls, culture):
        return culture.get(cls.Field.PREFERS) or []

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


class Prefer:
    class Field:
        TRADEGOOD = "tradegood"
        CULTURE = "culture"

    @classmethod
    def prefer2tradegood(cls, prefer):
        return prefer[cls.Field.TRADEGOOD]

    @classmethod
    def prefer2culture(cls, prefer):
        return prefer[cls.Field.CULTURE]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def list_all(cls):
        def _iter_all():
            for culture in Culture.list_all():
                yield from Culture.culture2prefers(culture)
        return list(_iter_all())

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_tradegood2prefers(cls):
        return GroupbyTool.dict_groupby_tree(cls.list_all(), [cls.prefer2tradegood])

    @classmethod
    def tradegood2prefers(cls, tradegood_codename):
        return cls._dict_tradegood2prefers().get(tradegood_codename) or []


# class PreferredTradegood:
#     class Field:
#         CODENAME = "codename"
#
#     @classmethod
#     def preferred_tradegood2codename(cls, obj):
#         return obj[cls.Field.CODENAME]

# class SpecialtyTradegood:
#     class Field:
#         CODENAME = "codename"
