import os

from future.utils import lmap
from itertools import chain

from foxylib.tools.collections.collections_tool import lchain

from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.port.port import Port
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDict, MarketpriceDoc
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.skill.price.price_skill import PriceSkill

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PriceByPort:

    @classmethod
    def port_lang2title(cls, port, lang):
        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"port_name": Port.port_lang2name(port, lang),
                }
        title = str2strip(HenriqueJinja2.textfile2text(filepath, data))
        return title

    @classmethod
    def port2text(cls, port_codename, tradegood_codename_list, marketprice_dict, lang):
        n = len(tradegood_codename_list)

        port = Port.codename2port(port_codename)
        str_title = cls.port_lang2title(port, lang)

        def tradegood2price(tradegood_codename):
            price = MarketpriceDict.lookup(marketprice_dict, port_codename, tradegood_codename)
            if price:
                return price

            price_fake = MarketpriceDoc.price_tradegood2doc_fake(port_codename, tradegood_codename)
            return price_fake

        price_list = lmap(tradegood2price, tradegood_codename_list)

        i_list_sorted = sorted(range(n), key=lambda i: MarketpriceDoc.key_default(price_list[i]))

        rows_body = [cls._price_lang2text(price_list[i], tradegood_codename_list[i], lang)
                     for i in i_list_sorted]

        return Rowsblock.rows2text(chain([str_title], rows_body))


    @classmethod
    def _price_lang2text(cls, price, tradegood_codename, lang):
        price_text = PriceSkill.price_lang2text(price, lang)
        tradegood_name = Tradegood.tradegood_lang2name(Tradegood.codename2tradegood(tradegood_codename), lang)
        return "{} {}".format(tradegood_name, price_text)

