import sys

from foxylib.tools.function.warmer import Warmer
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class AliasesEn:
    NAME = "aliases.en"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = SkillGooglesheets.sheetname2data_ll(cls.NAME)
        h = GooglesheetsTool.data_ll2dict_first_col2rest_cols(data_ll)
        return h


class AliasesKo:
    NAME = "aliases.ko"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = SkillGooglesheets.sheetname2data_ll(cls.NAME)
        h = GooglesheetsTool.data_ll2dict_first_col2rest_cols(data_ll)
        return h


class SkillGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "18D67KgdOwq1RbDP5mgIS8FzFAAOkQPCHbD8zcFRyoyQ"

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=10))
    def dict_lang2codename2aliases(cls):
        return {"en": AliasesEn.dict_codename2aliases(),
                "ko": AliasesKo.dict_codename2aliases(),
                }

WARMER.warmup()