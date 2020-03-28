import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port_entity import PortDoc
from henrique.main.entity.tradegood.tradegood_entity import TradegoodDoc

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortTradegoodResponse:
    @classmethod
    def tradegood_lang2response(cls, tg_codename, lang):

        ports = PortDoc.tradegood2docs(tg_codename)
        tradegood = TradegoodDoc.codename2doc(tg_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"tg_name": TradegoodDoc.doc_lang2name(tradegood, lang),
                "port_names": ", ".join([PortDoc.doc_lang2name(port, lang) for port in ports]),
                }
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

