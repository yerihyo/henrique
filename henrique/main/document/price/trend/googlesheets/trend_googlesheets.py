from functools import lru_cache

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class TextsEn:
    NAME = "texts.en"

    @classmethod
    def dict_codename2texts(cls):
        data_ll = TrendGooglesheets.sheetname2data_ll(cls.NAME)
        h = GooglesheetsTool.data_ll2dict_first_col2rest_cols(data_ll)
        return h

class TextsKo:
    NAME = "texts.ko"

    @classmethod
    def dict_codename2texts(cls):
        data_ll = TrendGooglesheets.sheetname2data_ll(cls.NAME)
        h = GooglesheetsTool.data_ll2dict_first_col2rest_cols(data_ll)
        return h


class TrendGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1nn0wseqV7QdUJLIgdB4fiISo4_nF-mm8zxppIlUA64w"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = [TextsEn.NAME, TextsKo.NAME]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]


    @classmethod
    def dict_lang2codename2texts(cls):
        return {"en": TextsEn.dict_codename2texts(),
                "ko": TextsKo.dict_codename2texts(),
                }
