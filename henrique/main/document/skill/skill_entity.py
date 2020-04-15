import os
import sys

from functools import lru_cache

from foxylib.tools.cache.cache_tool import CacheTool
from foxylib.tools.collections.iter_tool import iter2singleton
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import StringTool, str2lower
from henrique.main.document.henrique_entity import HenriqueEntity, Entity
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class HenriqueSkill:
    class Codename:
        PORT = "port"
        TRADEGOOD = "tradegood"
        CULTURE = "culture"
        PRICE = "price"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2class(cls, ):
        from henrique.main.skill.port.port_skill import PortSkill
        from henrique.main.skill.tradegood.tradegood_skill import TradegoodSkill
        from henrique.main.skill.culture.culture_skill import CultureSkill
        from henrique.main.skill.price.price_skill import PriceSkill

        h = {cls.Codename.PORT: PortSkill,
             cls.Codename.TRADEGOOD: TradegoodSkill,
             cls.Codename.CULTURE: CultureSkill,
             cls.Codename.PRICE: PriceSkill,
             }
        return h

    @classmethod
    def codename2class(cls, codename):
        return cls.dict_codename2class().get(codename)


class SkillEntity:

    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def entity2skill_code(cls, entity):
        return Entity.entity2value(entity)

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_lang2codename2aliases(cls):
        from henrique.main.document.skill.googlesheets.skill_googlesheets import SkillGooglesheets
        return SkillGooglesheets.dict_lang2codename2aliases()

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def codenames(cls):
        codename_sets = [set(h_codename2aliases.keys())
                         for lang, h_codename2aliases in cls.dict_lang2codename2aliases().items()]
        return iter2singleton(codename_sets)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        langs = HenriqueLocale.lang2langs_recognizable(lang)

        h_lang2codename2aliases = cls.dict_lang2codename2aliases()

        def codename2texts(codename):
            for lang in langs:
                aliases = JsonTool.down(h_lang2codename2aliases, [lang, codename])
                if not aliases:
                    continue

                yield from aliases

        h_codename2texts = {codename: list(codename2texts(codename))
                            for codename in cls.codenames()}

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm}
        matcher = GazetteerMatcher(h_codename2texts, config)
        return matcher


    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        lang = LocaleTool.locale2lang(Entity.Config.config2locale(config))

        span_value_list = cls.lang2matcher(lang).text2span_value_list(text_in)

        entity_list = [{Entity.Field.SPAN: span,
                        Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                        Entity.Field.VALUE: value,
                        Entity.Field.TYPE: cls.entity_type(),
                        }
                       for span, value in span_value_list]
        return entity_list







WARMER.warmup()
