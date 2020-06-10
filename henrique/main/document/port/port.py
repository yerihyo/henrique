import logging
import os
import sys
from functools import lru_cache

from future.utils import lmap
from itertools import chain

from foxylib.tools.collections.collections_tool import merge_dicts, luniq, DictTool, lchain
from foxylib.tools.collections.groupby_tool import dict_groupby_tree
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.native.native_tool import is_not_none
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class Port:
    class Field:
        CODENAME = "codename"
        CULTURE = "culture"
        ALIASES = "aliases"
        PRODUCTS = "products"
        COMMENTS = "comments"

    # @classmethod
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def _dict_codename2port_all_OLD(cls):
    #     from henrique.main.document.port.mongodb.port_doc import PortDoc
    #     h_mongo = PortDoc.dict_codename2port()
    #
    #     from henrique.main.document.port.googlesheets.port_googlesheets import PortGooglesheets
    #     h_googlesheets = PortGooglesheets.dict_codename2port()
    #
    #     codename_list = luniq(chain(h_googlesheets.keys(), h_mongo.keys(),))
    #
    #     def codename2port(codename):
    #         port = merge_dicts([h_mongo.get(codename) or {},
    #                             h_googlesheets.get(codename) or {},
    #                             ], vwrite=vwrite_update_if_identical,
    #                            )
    #         return port
    #
    #     dict_codename2port = merge_dicts([{codename: codename2port(codename)}
    #                                       for codename in codename_list],
    #                                      vwrite=vwrite_no_duplicate_key, )
    #     return dict_codename2port

    @classmethod
    def _dict_codename2port_all(cls):
        from henrique.main.document.port.googlesheets.port_googlesheets import PortGooglesheets
        return PortGooglesheets.dict_codename2port()


    @classmethod
    def list_all(cls):
        return list(cls._dict_codename2port_all().values())

    @classmethod
    def port2codename(cls, port):
        return port[cls.Field.CODENAME]

    @classmethod
    def port2culture(cls, port):
        return port[cls.Field.CULTURE]

    @classmethod
    def port2products(cls, port):
        return port.get(cls.Field.PRODUCTS) or []

    @classmethod
    def port_lang2aliases(cls, port, lang):
        return JsonTool.down(port, [cls.Field.ALIASES, lang])

    @classmethod
    def port_lang2comments(cls, port, lang):
        return JsonTool.down(port, [cls.Field.COMMENTS, lang])

    @classmethod
    def port_langs2aliases(cls, port, langs):
        return luniq(chain(*[cls.port_lang2aliases(port, lang) for lang in langs]))


    @classmethod
    def port_lang2name(cls, port, lang):
        return IterTool.first(cls.port_lang2aliases(port, lang))

    @classmethod
    def codename2port(cls, codename):
        return cls._dict_codename2port_all().get(codename)

    # @classmethod
    # def port_tradegood2is_sold(cls, port, tg_codename):
    #     products = cls.port2products(port)
    #
    #     for product in products:
    #         tg_codename_product = Product.product2tradegood(product)
    #         if tg_codename == tg_codename_product:
    #             return True
    #     return False

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_tradegood2ports(cls,):
        def h_tradegood2ports_iter():
            port_list = cls.list_all()
            # raise Exception({"port_list":port_list})

            for port in port_list:
                for product in cls.port2products(port):
                    yield {Product.product2tradegood(product): [port]}

        h_tg2ports_list = list(h_tradegood2ports_iter())
        h_tg2ports = merge_dicts(h_tg2ports_list, vwrite=DictTool.VWrite.extend)
        return h_tg2ports

    @classmethod
    def tradegood2ports(cls, tg_codename):
        return cls._dict_tradegood2ports().get(tg_codename) or []

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_culture2ports(cls,):
        h_culture2ports = merge_dicts([{cls.port2culture(port): [port]} for port in cls.list_all()],
                                      vwrite=DictTool.VWrite.extend)
        return h_culture2ports
        # return GroupbyTool.dict_groupby_tree(culture_port_iter(), [ig(0)])

    @classmethod
    def culture2ports(cls, culture_codename):
        return cls._dict_culture2ports().get(culture_codename) or []

    # @classmethod
    # @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    # def _dict_port2tradegoodtypes_resistant(cls,):
    #     logger = HenriqueLogger.func_level2logger(cls._dict_port2tradegoodtypes_resistant, logging.DEBUG)
    #     from henrique.main.document.tradegood.tradegood import Tradegood
    #
    #     def _port2tradegoodtypes_resistant(port):
    #         product_list = cls.port2products(port)
    #         if not product_list:
    #             return []
    #
    #         tradegood_codename_list = lmap(Product.product2tradegood, product_list)
    #         tradegood_list = lmap(Tradegood.codename2tradegood, tradegood_codename_list)
    #         tradegoodtype_list = list(Tradegood.tradegoods2types(tradegood_list))
    #         return tradegoodtype_list
    #
    #     h = {Port.port2codename(port): _port2tradegoodtypes_resistant(port)
    #          for port in cls.list_all()}
    #
    #     return h
    #
    # @classmethod
    # def port2tradegoodtypes_resistant(cls, port):
    #     h = cls._dict_port2tradegoodtypes_resistant()
    #     return h.get(port)


class Product:
    class Field:
        PORT = "port"
        TRADEGOOD = "tradegood"
        PRICE = "price"

    @classmethod
    def product2port(cls, product):
        return product.get(cls.Field.PORT)

    @classmethod
    def product2tradegood(cls, product):
        return product.get(cls.Field.TRADEGOOD)

    @classmethod
    def product2tradegoodtype(cls, product):
        from henrique.main.document.tradegood.tradegood import Tradegood
        tradegood = Tradegood.codename2tradegood(cls.product2tradegood(product))
        return Tradegood.tradegood2tradegoodtype(tradegood)

    @classmethod
    def product2price(cls, product):
        return product.get(cls.Field.PRICE)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def list_all(cls):
        return lchain(*map(Port.port2products, Port.list_all()))

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_port2products(cls):
        return dict_groupby_tree(cls.list_all(), [Product.product2port])

    @classmethod
    def port2products(cls, port_codename):
        return cls._dict_port2products().get(port_codename) or []

    # @classmethod
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def dict_tradegood2products(cls):
    #     return dict_groupby_tree(cls.list_all(), [Product.product2tradegood])

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_tradegoodtype2products(cls):
        return dict_groupby_tree(cls.list_all(), [Product.product2tradegoodtype])

    @classmethod
    def tradegoodtype2products(cls, tradegoodtype_codename):
        return cls._dict_tradegoodtype2products().get(tradegoodtype_codename) or []




WARMER.warmup()
