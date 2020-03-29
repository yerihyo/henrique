from functools import lru_cache
from google_auth_oauthlib.flow import InstalledAppFlow
from itertools import chain

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, luniq, \
    IterTool, DictTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.entity.culture.culture_entity import Culture
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h

class PreferredtradegoodSheet:
    NAME = "preferred_tradegood"

    @classmethod
    def dict_codename2tradegoods(cls):
        data_ll = CultureGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class CultureGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1s_EBQGNu0DlPedOXQNcfmE_LDk4wRq5QgJ9TsdBCCDE"


    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def flow(cls):
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly",
                  "https://www.googleapis.com/auth/spreadsheets",
                  ]
        flow = InstalledAppFlow.from_client_secrets_file(HenriqueGoogleapi.filepath_credentials(), scopes)
        return flow

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    @IterTool.f_iter2f_list
    def culture_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()
        h_codename2tradegoods = PreferredtradegoodSheet.dict_codename2tradegoods()

        codename_list = luniq(chain(h_codename2aliases_en.keys(),
                                    h_codename2aliases_ko.keys(),
                                    h_codename2tradegoods.keys(),
                                    )
                              )

        for codename in codename_list:
            aliases = DictTool.filter(lambda k,v:v,
                                      {"en": h_codename2aliases_en.get(codename),
                                       "ko": h_codename2aliases_ko.get(codename),
                                       })

            culture = {Culture.Field.CODENAME: codename,
                       Culture.Field.ALIASES: aliases,
                       Culture.Field.PREFERRED_TRADEGOODS: h_codename2tradegoods.get(codename),
                       }
            yield culture


