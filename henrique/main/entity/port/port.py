import os

from functools import lru_cache
from future.utils import lfilter
from itertools import chain

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, IterTool, luniq
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
    def dict_codename2port(cls):
        from henrique.main.entity.port.mongodb.port_doc import PortDoc
        h_mongo = PortDoc.dict_codename2port_partial()

        from henrique.main.entity.port.googlesheets.port_googlesheets import PortGooglesheets
        h_googlesheets = PortGooglesheets.dict_codename2port_partial()

        codename_list = luniq(chain(h_mongo.keys(), h_googlesheets.keys()))

        def codename2port(codename):
            port = merge_dicts([h_mongo.get(codename) or {},
                                h_googlesheets.get(codename) or {},
                                ], vwrite=vwrite_no_duplicate_key,
                               )
            return port

        dict_codename2port = merge_dicts([{codename: codename2port(codename)}
                                          for codename in codename_list],
                                         vwrite=vwrite_no_duplicate_key, )
        return dict_codename2port


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
    def port_lang2name(cls, port, lang):
        return IterTool.first(cls.port_lang2aliases(port, lang))

    @classmethod
    def codename2port(cls, codename):
        return cls.dict_codename2port().get(codename)

    @classmethod
    def port_tradegood2is_sold(cls, port, tg_codename):
        products = cls.port2products(port)

        for product in products:
            tg_codename_product = Product.product2tradegood_codename(product)
            if tg_codename == tg_codename_product:
                return True
        return False

    @classmethod
    def tradegood2ports(cls, tg_codename):
        dict_codename2port = cls.dict_codename2port()
        return lfilter(lambda port: cls.port_tradegood2is_sold(port, tg_codename), dict_codename2port.values())


    @classmethod
    def culture2ports(cls, culture_codename):
        dict_codename2port = cls.dict_codename2port()
        return lfilter(lambda port: cls.port2culture(port) == culture_codename, dict_codename2port.values())


class Product:
    @classmethod
    def product2tradegood_codename(cls, product):
        return JsonTool.down(product, ["name", "en"])



