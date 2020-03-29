from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.entity.port.port_entity import Port
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class CultureSheet:
    NAME = "culture"

    @classmethod
    def dict_codename2culture(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class PortGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1DxaBuSsOvAf4nsy4n2XNwcmPVqBLRvWgCbs5Y8AHFtE"

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    def dict_codename2port_partial(cls):
        h_codname2culture = CultureSheet.dict_codename2culture()

        h = merge_dicts([{codename: {Port.Field.CULTURE: culture}}
                         for codename, culture in h_codname2culture.items()],
                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                        )
        return h
