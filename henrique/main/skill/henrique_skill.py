import os

from future.utils import lmap, lfilter
from itertools import chain

from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import str2lower, str2strip, StringTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class HenriqueSkill:
    class Code:
        PORT = "port"
        TRADEGOOD = "tradegood"

        @classmethod
        def all(cls):
            return {cls.PORT, cls.TRADEGOOD, }


    @classmethod
    def yaml(cls):
        filepath = os.path.join(FILE_DIR, "skill.yaml")
        return YAMLTool.filepath2j(filepath)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def matcher(cls):
        config = {GazetteerMatcher.Config.Key.NORMALIZER: str2lower}
        matcher = GazetteerMatcher(cls.yaml(),config=config)
        return matcher

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2class(cls, ):
        from henrique.main.skill.port.port_skill import PortSkill
        h = {cls.Code.PORT: PortSkill,
             }
        return h

    @classmethod
    def count(cls):
        return len(cls.dict_codename2class())

    @classmethod
    def codename2class(cls, name):
        h = cls.dict_codename2class()
        return h.get(name)




class Rowsblock:
    @classmethod
    def rows2text(cls, rows):
        return "\n".join(lfilter(bool, map(str2strip, rows)))

    @classmethod
    def blocks2text(cls, blocks):
        return "\n\n".join(lfilter(bool, map(str2strip, blocks)))

    @classmethod
    def text2norm(cls, text_in):
        if not text_in:
            return text_in

        text_out = StringTool.str2strip_eachline(StringTool.str2strip(text_in))
        return text_out
