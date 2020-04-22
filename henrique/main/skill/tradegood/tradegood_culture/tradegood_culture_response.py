import os

from future.utils import lmap

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture, Prefer
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodCultureResponse:
    @classmethod
    def codename_lang2text(cls, culture_codename, lang):
        culture = Culture.codename2culture(culture_codename)
        prefers = Culture.culture2prefers(culture)

        def prefer2data(prefer):
            tg = Tradegood.codename2tradegood(Prefer.prefer2tradegood(prefer))

            h = {"name": Tradegood.tradegood_lang2name(tg, lang),
                 }
            return h

        data = {"culture_name": Culture.culture_lang2name(culture, lang),
                "preferred_tradegood_data_list": lmap(prefer2data, prefers),
                }

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

