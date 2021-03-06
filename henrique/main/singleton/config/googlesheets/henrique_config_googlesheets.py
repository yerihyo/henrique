from functools import lru_cache

from future.utils import lfilter

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.singleton.config.henrique_config import HenriqueConfig
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi
from khala.document.chatroom.chatroom import Chatroom


class HenriqueSheet:
    NAME = "henrique"

    @classmethod
    def config_list(cls):
        data_ll = HenriqueConfigGooglesheets.sheetname2data_ll(cls.NAME)
        top_row = data_ll[0]

        def row2config(row):
            config = merge_dicts([{col_top: str2strip(row[i])}
                                    for i, col_top in enumerate(top_row)],
                                   vwrite=vwrite_no_duplicate_key)

            return config

        config_list = lfilter(bool, map(row2config, data_ll[1:]))
        return config_list


class HenriqueConfigGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "11XXks43hhrBJX5q0MRU4dQobTiIMsYJ8qtIQdfkLljQ"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = [HenriqueSheet.NAME,]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    def config_list(cls):
        return HenriqueSheet.config_list()
