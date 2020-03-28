import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.tradegood.tradegood_entity import TradegoodDoc

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortTradegoodResponse:
    @classmethod
    def codename_lang2response(cls, tradegood_codename, lang):
        tradegood_doc = TradegoodDoc.key2doc(tradegood_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"name": TradegoodDoc.doc_lang2name(tradegood_doc, lang)}
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

