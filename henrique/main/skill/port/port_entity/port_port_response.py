import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.port.port_entity import PortDoc

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortPortResponse:
    @classmethod
    def code_lang2response(cls, port_codename, lang):
        port_doc = PortDoc.codename2doc(port_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"name": PortDoc.doc_lang2name(port_doc, lang)}
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

