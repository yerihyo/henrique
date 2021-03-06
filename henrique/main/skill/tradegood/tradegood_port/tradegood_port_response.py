import os

from future.utils import lmap

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodPortResponse:
    @classmethod
    def codename_lang2text(cls, port_codename, lang):
        port = Port.codename2port(port_codename)
        products = Port.port2products(port)

        # ports = Tradegood.port2tradegoods(port_codename)
        # tradegood = Tradegood.codename2tradegood(tg_codename)
        # assert_is_not_none(tradegood_doc, tg_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        def product2data(product):
            tg_codename = Product.product2tradegood(product)
            tg = Tradegood.codename2tradegood(tg_codename)

            h = {"name": Tradegood.tradegood_lang2name(tg, lang),
                 }
            return h

        data = {"port_name": Port.port_lang2name(port, lang),
                "product_data_list": lmap(product2data, products),
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

