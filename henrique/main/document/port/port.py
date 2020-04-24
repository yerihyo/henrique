import os
from operator import itemgetter as ig

from functools import lru_cache
from future.utils import lfilter
from itertools import chain

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, luniq, DictTool, \
    vwrite_update_if_identical
from foxylib.tools.collections.groupby_tool import GroupbyTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class Port:
    class Field:
        CODENAME = "codename"
        CULTURE = "culture"
        ALIASES = "aliases"
        PRODUCTS = "products"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2port_all(cls):
        from henrique.main.document.port.mongodb.port_doc import PortDoc
        h_mongo = PortDoc.dict_codename2port_partial()

        from henrique.main.document.port.googlesheets.port_googlesheets import PortGooglesheets
        h_googlesheets = PortGooglesheets.dict_codename2port_partial()

        codename_list = luniq(chain(h_googlesheets.keys(), h_mongo.keys(),))

        def codename2port(codename):
            port = merge_dicts([h_mongo.get(codename) or {},
                                h_googlesheets.get(codename) or {},
                                ], vwrite=vwrite_update_if_identical,
                               )
            return port

        dict_codename2port = merge_dicts([{codename: codename2port(codename)}
                                          for codename in codename_list],
                                         vwrite=vwrite_no_duplicate_key, )
        return dict_codename2port

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
    def _dict_tradegood2ports(cls,):
        def h_tradegood2ports_iter():
            for port in cls.list_all():
                for product in cls.port2products(port):
                    yield {Product.product2tradegood(product): [port]}

        h_tg2ports_list = list(h_tradegood2ports_iter())
        h_tg2ports = merge_dicts(h_tg2ports_list, vwrite=DictTool.VWrite.extend)
        # raise Exception(h_tg2ports)
        return h_tg2ports

    @classmethod
    def tradegood2ports(cls, tg_codename):
        return cls._dict_tradegood2ports().get(tg_codename) or []

    @classmethod
    def _dict_culture2ports(cls, ):
        h_culture2ports = merge_dicts([{cls.port2culture(port): [port]} for port in cls.list_all()],
                                      vwrite=DictTool.VWrite.extend)
        return h_culture2ports
        # return GroupbyTool.dict_groupby_tree(culture_port_iter(), [ig(0)])

    @classmethod
    def culture2ports(cls, culture_codename):
        return cls._dict_culture2ports().get(culture_codename) or []


class Product:
    class Field:
        TRADEGOOD = "tradegood"

    @classmethod
    def product2tradegood(cls, product):
        return product.get(cls.Field.TRADEGOOD)




