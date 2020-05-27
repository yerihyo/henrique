import sys

from foxylib.tools.function.warmer import Warmer
from functools import lru_cache

from future.utils import lmap
from itertools import chain

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, luniq
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = ServerGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = ServerGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class ServerGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1z_8oCBFUj5ArGr8WvQFio3-uoQgbAOC87BupNNAF0_M"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = [NameskoSheet.NAME, NamesenSheet.NAME]
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
    def server_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()

        codename_list = luniq(chain(h_codename2aliases_en.keys(),
                                    h_codename2aliases_ko.keys(),
                                    )
                              )

        def codename2server(codename):
            aliases = DictTool.filter(lambda k, v: v,
                                      {"en": h_codename2aliases_en.get(codename),
                                       "ko": h_codename2aliases_ko.get(codename),
                                       })

            culture = {Server.Field.CODENAME: codename,
                       Server.Field.ALIASES: aliases,
                       }
            return DictTool.filter(lambda k, v: v, culture)

        return lmap(codename2server, codename_list)


WARMER.warmup()
