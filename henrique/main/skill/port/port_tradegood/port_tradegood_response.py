import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port_entity import Port
from henrique.main.entity.tradegood.tradegood import Tradegood
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortTradegoodResponse:
    @classmethod
    def codename_lang2response(cls, tg_codename, lang):

        ports = Port.tradegood2ports(tg_codename)
        tradegood = Tradegood.codename2tradegood(tg_codename)
        # assert_is_not_none(tradegood_doc, tg_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"tg_name": Tradegood.tradegood_lang2name(tradegood, lang),
                "port_names": ", ".join([Port.port_lang2name(port, lang) for port in ports]),
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

