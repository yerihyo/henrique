import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.port.port_entity import Port
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.khala.henrique_khala import Rowsblock

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortTradegoodResponse:
    class Field:
        TRADEGOOD_NAME = "tradegood_name"
        PORT_NAMES = "port_names"

    @classmethod
    def codename_lang2json(cls, tradegood_codename, lang):
        ports = Port.tradegood2ports(tradegood_codename)
        tradegood = Tradegood.codename2tradegood(tradegood_codename)

        data = {cls.Field.TRADEGOOD_NAME: Tradegood.tradegood_lang2name(tradegood, lang),
                cls.Field.PORT_NAMES: sorted([Port.port_lang2name(port, lang) for port in ports],)
                }
        return data

    @classmethod
    def codename_lang2text(cls, culture_codename, lang):
        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = cls.codename_lang2json(culture_codename, lang)
        text_out = HenriqueJinja2.textfile2text(filepath, data)
        return Rowsblock.text2norm(text_out)


