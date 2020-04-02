import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port import Port
from henrique.main.entity.price.price import PriceDict
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
        title = cls.tradegood_lang2title(tradegood, lang)

        str_portlikes = "\n".join([cls._entity_pair2response(tradegood_codename, port_codename, price_dict, lang)
                                   for port_codename in port_codename_list])

        return "\n".join([title, str_portlikes])


    @classmethod
    def _entity_pair2response(cls, tradegood_codename, port_codename, price_dict, lang):
        port = Port.codename2port(port_codename)
        port_name = Port.port_lang2name(port, lang)

        price = PriceDict.lookup(price_dict, port_codename, tradegood_codename)
        price_text = PriceSkill.price_lang2text(price, lang)
        return "[{}] {}".format(port_name, price_text)

