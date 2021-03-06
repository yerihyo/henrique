import logging
import sys

from cachetools import cached, TTLCache
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
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    @cached(cache=TTLCache(maxsize=2, ttl=60 * 10))
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    @cached(cache=TTLCache(maxsize=2, ttl=60 * 10))
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h

class PrefersSheet:
    NAME = "prefers"

    @classmethod
    @cached(cache=TTLCache(maxsize=2, ttl=60 * 10))
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
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

    @classmethod
    @cached(cache=TTLCache(maxsize=2, ttl=60 * 10))
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = [NameskoSheet.NAME, NamesenSheet.NAME, PrefersSheet.NAME]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    def culture_list_all(cls):
        logger = HenriqueLogger.func_level2logger(cls.culture_list_all, logging.DEBUG)

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

        list_all = lmap(codename2culture, codename_list)
        # logger.debug({"list_all":list_all})

        return list_all

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @cached(cache=TTLCache(maxsize=2, ttl=60 * 10))
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2culture(cls):
        culture_list = cls.culture_list_all()
        assert_is_not_none(culture_list)

        h_codename2culture = merge_dicts([{Culture.culture2codename(culture): culture}
                                          for culture in culture_list])
        return h_codename2culture

# WARMER.warmup()
