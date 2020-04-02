import os

from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port import Port
from henrique.main.entity.price.price import PriceDict
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
    def port2response(cls, port_codename, tradegood_codename_list, price_dict, lang):

        port = Port.codename2port(port_codename)
        str_title = cls.port_lang2title(port, lang)

        str_body = "\n".join([cls._entity_pair2response(port_codename, tg_codename, price_dict, lang)
                              for tg_codename in tradegood_codename_list])
        return "\n".join([str_title, str_body])


    @classmethod
    def _entity_pair2response(cls, tradegood_codename, port_codename, price_dict, lang):
        tradegood = Tradegood.codename2tradegood(tradegood_codename)
        tradegood_name = Tradegood.tradegood_lang2name(tradegood, lang)

        price = PriceDict.lookup(price_dict, port_codename, tradegood_codename)
        price_text = PriceSkill.price_lang2text(price, lang)
        return "[{}] {}".format(tradegood_name, price_text)

