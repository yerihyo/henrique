import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.culture.culture import Culture
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.khala.henrique_khala import Rowsblock

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortCultureResponse:
    class Field:
        CULTURE_NAME = "culture_name"
        PORT_NAMES = "port_names"

    @classmethod
    def data2culture_name(cls, data):
        return data[cls.Field.CULTURE_NAME]

    @classmethod
    def data2port_names(cls, data):
        return data[cls.Field.PORT_NAMES]

    @classmethod
    def data2norm_unittest(cls, data):
        return {cls.Field.CULTURE_NAME: cls.data2culture_name(data),
                cls.Field.PORT_NAMES: set(cls.data2port_names(data)),
                }

    @classmethod
    def codename_lang2json(cls, culture_codename, lang):
        ports = Port.culture2ports(culture_codename)
        culture = Culture.codename2culture(culture_codename)

        data = {cls.Field.CULTURE_NAME: Culture.culture_lang2name(culture, lang),
                cls.Field.PORT_NAMES: [Port.port_lang2name(port, lang) for port in ports],
                }
        return data

    @classmethod
    def codename_lang2text(cls, culture_codename, lang):
        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = cls.codename_lang2json(culture_codename, lang)
        text_out = HenriqueJinja2.textfile2text(filepath, data)
        return Rowsblock.text2norm(text_out)
