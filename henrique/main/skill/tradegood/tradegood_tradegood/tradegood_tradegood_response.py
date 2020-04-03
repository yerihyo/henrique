import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port_entity import Port
from henrique.main.entity.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodTradegoodResponse:
    @classmethod
    def codename_lang2text(cls, tradegood_codename, lang):
        tradegood = Tradegood.codename2tradegood(tradegood_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"name": Tradegood.tradegood_lang2name(tradegood, lang)}
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

