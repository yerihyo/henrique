from operator import itemgetter as ig

from future.utils import lmap
from itertools import chain

from functools import lru_cache

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, luniq
from foxylib.tools.collections.groupby_tool import dict_groupby_tree, gb_tree_global
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class NameskoSheet:
    NAME = "names.ko"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class NamesenSheet:
    NAME = "names.en"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class CultureSheet:
    NAME = "culture"

    @classmethod
    def dict_codename2culture(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class ProductSheet:
    NAME = "product"

    @classmethod
    def dict_codename2products(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h_raw = gb_tree_global(data_ll[1:], [ig(0)])

        def row2product(row):
            tradegood = row[1]
            price = row[2] if len(row) >= 3 else None
            raw = {Product.Field.TRADEGOOD: tradegood,
                       Product.Field.PRICE: price,
                       }
            product = DictTool.filter(lambda k,v:v, raw)
            return product

        h = {k:lmap(row2product, l)
             for k, l in h_raw.items()}

        return h

class PortGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1DxaBuSsOvAf4nsy4n2XNwcmPVqBLRvWgCbs5Y8AHFtE"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=10))
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    def dict_codename2port_partial(cls):
        h_codename2culture = CultureSheet.dict_codename2culture()

        def codename_culture2port_partial(codename, culture):
            h = {Port.Field.CODENAME: codename,
                 Port.Field.CULTURE: culture,
                 }
            return h
        h = merge_dicts([{codename: codename_culture2port_partial(codename,culture)}
                         for codename, culture in h_codename2culture.items()],
                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                        )
        return h


    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def port_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()
        h_codename2culture = CultureSheet.dict_codename2culture()
        h_codename2product_list = ProductSheet.dict_codename2products()

        codename_list = luniq(chain(h_codename2aliases_en.keys(),
                                    h_codename2aliases_ko.keys(),
                                    )
                              )

        def codename2port(codename):
            aliases = DictTool.filter(lambda k, v: v,
                                      {"en": h_codename2aliases_en.get(codename),
                                       "ko": h_codename2aliases_ko.get(codename),
                                       })
            culture = h_codename2culture[codename]
            product_list = h_codename2product_list.get(codename)

            port = {Port.Field.CODENAME: codename,
                    Port.Field.CULTURE: culture,
                    Port.Field.ALIASES: aliases,
                    Port.Field.PRODUCTS: product_list,
                    }
            return DictTool.filter(lambda k, v: v, port)

        return lmap(codename2port, codename_list)

