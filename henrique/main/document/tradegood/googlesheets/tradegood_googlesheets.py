import sys
from operator import itemgetter as ig

from future.utils import lmap
from itertools import chain

from functools import lru_cache

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, luniq
from foxylib.tools.collections.groupby_tool import dict_groupby_tree, gb_tree_global
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = TradegoodGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = TradegoodGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class TradegoodtypeSheet:
    NAME = "tradegoodtype"

    @classmethod
    def dict_codename2tradegoodtype(cls):
        data_ll = TradegoodGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1]} for row in data_ll[1:] if len(row)>1],
                        vwrite=vwrite_no_duplicate_key)
        return h


class TradegoodGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1XgTitp7h-oeAIzaxlLkQx1KX4c2uk4-izwn6W5ke290"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = [NameskoSheet.NAME, NamesenSheet.NAME, TradegoodtypeSheet.NAME]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2tradegood(cls):
        tradegood_list_all = cls.tradegood_list_all()
        h = merge_dicts([{Tradegood.tradegood2codename(tradegood): tradegood} for tradegood in tradegood_list_all],
                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                        )
        return h


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def tradegood_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()
        h_codename2tradegoodtype = TradegoodtypeSheet.dict_codename2tradegoodtype()
        # raise Exception({"h_codename2product_list":h_codename2product_list})

        codename_list = luniq(chain(h_codename2aliases_en.keys(),
                                    h_codename2aliases_ko.keys(),
                                    )
                              )

        def codename2port(codename):
            aliases = DictTool.filter(lambda k, v: v,
                                      {"en": h_codename2aliases_en.get(codename),
                                       "ko": h_codename2aliases_ko.get(codename),
                                       })
            tradegoodtype = h_codename2tradegoodtype.get(codename)

            port = DictTool.filter(lambda k, v: bool(v),
                                   {Tradegood.Field.CODENAME: codename,
                                    Tradegood.Field.TRADEGOODTYPE: tradegoodtype,
                                    Tradegood.Field.ALIASES: aliases,
                                    }
                                   )
            return DictTool.filter(lambda k, v: v, port)

        return lmap(codename2port, codename_list)


WARMER.warmup()
