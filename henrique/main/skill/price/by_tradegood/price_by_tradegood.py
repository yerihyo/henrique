import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port import Port
from henrique.main.entity.price.price import PriceDict, Price
from henrique.main.entity.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
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
    def tradegood2response(cls, tradegood_codename, port_codename_list, price_dict, lang):
        tradegood = Tradegood.codename2tradegood(tradegood_codename)
        str_title = cls.tradegood_lang2title(tradegood, lang)

        price_list_raw = [PriceDict.lookup(price_dict, port_codename, tradegood_codename)
                          for port_codename in port_codename_list]

        price_list = sorted(price_list_raw, key=Price.key_default)

        str_body = "\n".join([cls._price_lang2text(price, lang)
                              for price in price_list])

        return "\n".join([str_title, str_body])

    @classmethod
    def _price_lang2text(cls, price, lang):
        price_text = PriceSkill.price_lang2text(price, lang)
        port_name = Port.port_lang2name(Port.codename2port(Price.price2port(price)), lang)
        return "{} {}".format(port_name, price_text)

