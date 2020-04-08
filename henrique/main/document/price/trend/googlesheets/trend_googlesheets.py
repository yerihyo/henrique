from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class TextsEn:
    NAME = "texts.en"

    @classmethod
    def dict_codename2texts(cls):
        data_ll = TrendGooglesheets.sheetname2data_ll(cls.NAME)
        h = TrendGooglesheets.data_ll2dict_codename2texts(data_ll)
        return h

class TextsKo:
    NAME = "texts.ko"

    @classmethod
    def dict_codename2texts(cls):
        data_ll = TrendGooglesheets.sheetname2data_ll(cls.NAME)
        h = TrendGooglesheets.data_ll2dict_codename2texts(data_ll)
        return h


class TrendGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1nn0wseqV7QdUJLIgdB4fiISo4_nF-mm8zxppIlUA64w"

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    def data_ll2dict_codename2texts(cls, data_ll):
        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


    @classmethod
    def dict_lang2codename2texts(cls):
        return {"en": TextsEn.dict_codename2texts(),
                "ko": TextsKo.dict_codename2texts(),
                }
