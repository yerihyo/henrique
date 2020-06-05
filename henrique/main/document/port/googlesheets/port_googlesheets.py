import sys
from operator import itemgetter as ig

from cachetools import LRUCache
from future.utils import lmap, lfilter
from itertools import chain

from functools import lru_cache

from foxylib.tools.cache.cache_manager import CacheManager
from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, luniq, zip_strict
from foxylib.tools.collections.groupby_tool import dict_groupby_tree, gb_tree_global
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool, GooglesheetsErrorcheck
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

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

        port2row_list = gb_tree_global(data_ll[1:], [ig(0)])

        def row2product(row):
            port, tradegood = row[0], row[1]
            price = row[2] if len(row) >= 3 else None
            raw = {Product.Field.PORT: port,
                   Product.Field.TRADEGOOD: tradegood,
                   Product.Field.PRICE: price,
                   }
            product = DictTool.filter(lambda k,v:v, raw)
            return product

        h = {port: lmap(row2product, row_list)
             for port, row_list in port2row_list}

        return h


class CommentsKoSheet:
    NAME = "comments.ko"

    @classmethod
    def dict_codename2comments(cls):
        data_ll = PortGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: lfilter(bool,row[1:])} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return DictTool.filter(lambda k,v:bool(v), h)


class PortGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1DxaBuSsOvAf4nsy4n2XNwcmPVqBLRvWgCbs5Y8AHFtE"

    @classmethod
    def _dict_sheetname2data_ll(cls, ):
        sheetname_list = [NameskoSheet.NAME, NamesenSheet.NAME,
                          CommentsKoSheet.NAME,
                          CultureSheet.NAME, ProductSheet.NAME,
                          ]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=2),)
    def dict_sheetname2data_ll(cls,):
        return cls._dict_sheetname2data_ll()

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2port(cls):
        port_list_all = cls.port_list_all()
        h = merge_dicts([{Port.port2codename(port): port} for port in port_list_all],
                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                        )
        return h


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def port_list_all(cls):
        h_codename2aliases_en = NamesenSheet.dict_codename2aliases()
        h_codename2aliases_ko = NameskoSheet.dict_codename2aliases()
        h_codename2culture = CultureSheet.dict_codename2culture()
        h_codename2product_list = ProductSheet.dict_codename2products()
        h_codename2comments_ko = CommentsKoSheet.dict_codename2comments()
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

            comments = DictTool.filter(lambda k, v: v,
                                      {"ko": h_codename2comments_ko.get(codename),
                                       })

            port = {Port.Field.CODENAME: codename,
                    Port.Field.CULTURE: h_codename2culture[codename],
                    Port.Field.ALIASES: aliases,
                    Port.Field.PRODUCTS: h_codename2product_list.get(codename),
                    Port.Field.COMMENTS: comments,
                    }
            return DictTool.filter(lambda k, v: v, port)

        return lmap(codename2port, codename_list)


class Endpoint:
    @classmethod
    def _checkerror_items(cls):
        h_sheetname2table = PortGooglesheets._dict_sheetname2data_ll()
        GooglesheetsErrorcheck.table_list2dict_duplicates(h_sheetname2table, )
        raise NotImplementedError()

    @classmethod
    def checkerror(cls):
        report_list = list(cls._checkerror_items())
        return "\n".join(report_list)


WARMER.warmup()
