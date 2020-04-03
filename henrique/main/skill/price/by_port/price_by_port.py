import os

from foxylib.tools.collections.collections_tool import lchain

from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port import Port
from henrique.main.entity.price.price import PriceDict, Price
from henrique.main.entity.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
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
    def port2response_block(cls, port_codename, tradegood_codename_list, price_dict, lang):

        port = Port.codename2port(port_codename)
        str_title = cls.port_lang2title(port, lang)

        price_list_raw = [PriceDict.lookup(price_dict, port_codename, tradegood_codename)
                          for tradegood_codename in tradegood_codename_list]

        price_list = sorted(price_list_raw, key=Price.key_default)

        rows_body = [cls._price_lang2text(price, lang)
                              for price in price_list]

        return {PriceSkill.ResponseBlock.Field.TITLE: str_title,
                PriceSkill.ResponseBlock.Field.ROWS: rows_body,
                }


    @classmethod
    def _price_lang2text(cls, price, lang):
        price_text = PriceSkill.price_lang2text(price, lang)
        tradegood_name = Tradegood.tradegood_lang2name(Tradegood.codename2tradegood(Price.price2tradegood(price)), lang)
        return "{} {}".format(tradegood_name, price_text)

