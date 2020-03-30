import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from foxylib.tools.string.string_tool import str2strip
from henrique.main.entity.culture.culture_entity import Culture

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class CultureCultureResponse:
    @classmethod
    def codename_lang2response(cls, culture_codename, lang):
        culture = Culture.codename2culture(culture_codename)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"name": Culture.culture_lang2name(culture, lang)}
        text_out = str2strip(Jinja2Renderer.textfile2text(filepath, data))

        return text_out

