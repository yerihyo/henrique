import os

from future.utils import lmap

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.culture.culture import Culture, PreferredTradegood
from henrique.main.entity.port.port import Product
from henrique.main.entity.port.port_entity import Port
from henrique.main.entity.tradegood.tradegood import Tradegood

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodCultureResponse:
    @classmethod
    def codename_lang2response(cls, culture_codename, lang):
        culture = Culture.codename2culture(culture_codename)
        preferred_tradegoods = Culture.culture2preferred_tradegoods(culture)

        def preferred_tradegood2data(preferred_tradegood):
            tg_codename = PreferredTradegood.preferred_tradegood2codename(preferred_tradegood)
            tg = Tradegood.codename2tradegood(tg_codename)

            h = {"name": Tradegood.tradegood_lang2name(tg, lang),
                 }
            return h

        data = {"culture_name": Culture.culture_lang2name(culture, lang),
                "preferred_tradegood_data_list": lmap(preferred_tradegood2data, preferred_tradegoods),
                }

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

