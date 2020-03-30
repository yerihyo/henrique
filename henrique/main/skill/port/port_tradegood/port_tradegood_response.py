import os

from nose.tools import assert_is_not_none

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port_entity import Port
from henrique.main.entity.tradegood.tradegood_entity import TradegoodDoc

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortTradegoodResponse:
    @classmethod
    def codename_lang2response(cls, tg_codename, lang):

        ports = Port.tradegood2ports(tg_codename)
        tradegood_doc = TradegoodDoc.codename2doc(tg_codename)
        # assert_is_not_none(tradegood_doc, tg_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"tg_name": TradegoodDoc.doc_lang2name(tradegood_doc, lang),
                "port_names": ", ".join([Port.port_lang2name(port, lang) for port in ports]),
                }
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

