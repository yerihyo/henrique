import os

from future.utils import lmap

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.culture.culture import Culture, Prefer
from henrique.main.entity.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class CultureTradegoodResponse:
    @classmethod
    def codename_lang2text(cls, tradegood_codename, lang):
        tradegood = Tradegood.codename2tradegood(tradegood_codename)

        prefer_list = Prefer.tradegood2prefers(tradegood_codename)

        def prefer2data(prefer):
            culture = Culture.codename2culture(Prefer.prefer2culture(prefer))
            culture_name = Culture.culture_lang2name(culture, lang)
            return {"culture_name":culture_name}

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"tradegood_name": Tradegood.tradegood_lang2name(tradegood, lang),
                "prefer_data_list": lmap(prefer2data, prefer_list),
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

