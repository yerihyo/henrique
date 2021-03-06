import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class CulturePortResponse:
    @classmethod
    def codename_lang2text(cls, port_codename, lang):

        port = Port.codename2port(port_codename)
        culture = Culture.codename2culture(Port.port2culture(port))

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"culture_name": Culture.culture_lang2name(culture, lang),
                "port_name": Port.port_lang2name(port, lang)
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

