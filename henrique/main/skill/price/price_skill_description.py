from functools import lru_cache

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class PriceSkillDescription:
    @classmethod
    def sheetname(cls):
        return "price"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_lang2text(cls, ):
        from henrique.main.skill.help.help_skill import HelpSkill

        credentials = HenriqueGoogleapi.credentials()
        spreadsheet_id = HelpSkill.spreadsheet_id()
        data_ll = GooglesheetsTool.cred_id_name2data_ll(credentials, spreadsheet_id, cls.sheetname())

        h_lang2text = merge_dicts([{row[0]: row[1]} for row in data_ll[1:]],
                                  vwrite=vwrite_no_duplicate_key)

        return h_lang2text

    @classmethod
    def lang2text(cls, lang):
        return cls.dict_lang2text().get(lang)
