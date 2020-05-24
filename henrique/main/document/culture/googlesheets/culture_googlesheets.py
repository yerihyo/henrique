import sys

from functools import lru_cache

from future.utils import lmap
from itertools import chain
from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, luniq, \
    DictTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.culture.culture import Culture, Prefer
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h

class PrefersSheet:
    NAME = "prefers"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2prefers(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        def row2prefers(row):
            culture_codename = row[0]
            preferred_tradegoods = [{Prefer.Field.TRADEGOOD: tg_codename,
                                     Prefer.Field.CULTURE: culture_codename,
                                     }
                                    for tg_codename in row[1:]]
            return preferred_tradegoods

        h = merge_dicts([{row[0]: row2prefers(row)}
                         for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class CultureGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1s_EBQGNu0DlPedOXQNcfmE_LDk4wRq5QgJ9TsdBCCDE"


    # @classmethod
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def flow(cls):
    #     scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly",
    #               "https://www.googleapis.com/auth/spreadsheets",
    #               ]
    #     flow = InstalledAppFlow.from_client_secrets_file(HenriqueGoogleapi.filepath_credentials(), scopes)
    #     return flow

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    def culture_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()
        h_codename2prefers = PrefersSheet.dict_codename2prefers()

        codename_list = luniq(chain(h_codename2aliases_en.keys(),
                                    h_codename2aliases_ko.keys(),
                                    h_codename2prefers.keys(),
                                    )
                              )

        def codename2culture(codename):
            aliases = DictTool.filter(lambda k,v:v,
                                      {"en": h_codename2aliases_en.get(codename),
                                       "ko": h_codename2aliases_ko.get(codename),
                                       })

            culture = {Culture.Field.CODENAME: codename,
                       Culture.Field.ALIASES: aliases,
                       Culture.Field.PREFERS: h_codename2prefers.get(codename) or [],
                       }
            return DictTool.filter(lambda k, v: v, culture)

        return lmap(codename2culture, codename_list)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2culture(cls):
        culture_list = cls.culture_list_all()
        assert_is_not_none(culture_list)

        h_codename2culture = merge_dicts([{Culture.culture2codename(culture): culture}
                                          for culture in culture_list])
        return h_codename2culture

WARMER.warmup()
