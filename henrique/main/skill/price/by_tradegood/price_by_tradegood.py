import os

from future.utils import lmap
from itertools import chain

from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.port.port import Port
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDict, MarketpriceDoc
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.skill.price.price_skill import PriceSkill

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PriceByTradegood:

    @classmethod
    def tradegood_lang2title(cls, tradegood, lang):
        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"tradegood_name": Tradegood.tradegood_lang2name(tradegood, lang),
                }
        title = str2strip(HenriqueJinja2.textfile2text(filepath, data))
        return title

    @classmethod
    def tradegood2text(cls, tradegood_codename, port_codename_list, price_dict, lang):

        n = len(port_codename_list)
        tradegood = Tradegood.codename2tradegood(tradegood_codename)
        str_title = cls.tradegood_lang2title(tradegood, lang)

        def port2price(port_codename):
            price = MarketpriceDict.lookup(price_dict, port_codename, tradegood_codename)
            if price:
                return price

            price_fake = MarketpriceDoc.price_tradegood2doc_fake(port_codename, tradegood_codename)
            return price_fake

        price_list = lmap(port2price, port_codename_list)

        i_list_sorted = sorted(range(n), key=lambda i: MarketpriceDoc.key_default(price_list[i]))
        # price_list = sorted(price_list_raw, key=MarketpriceDoc.key_default)

        rows_body = [cls._price_lang2text(price_list[i], port_codename_list[i], lang)
                     for i in i_list_sorted]

        return Rowsblock.rows2text(chain([str_title], rows_body, ))


    @classmethod
    def _price_lang2text(cls, price, port_codename, lang):
        price_text = PriceSkill.price_lang2text(price, lang)
        port_name = Port.port_lang2name(Port.codename2port(port_codename), lang)
        return "{} {}".format(port_name, price_text)

