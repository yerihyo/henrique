import os
import sys
from operator import itemgetter as ig

import re
from foxylib.tools.cache.cache_tool import CacheTool
from functools import lru_cache, partial
from future.utils import lmap

from foxylib.tools.collections.collections_tool import l_singleton2obj
from foxylib.tools.collections.iter_tool import iter2singleton
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import StringTool, str2lower
from henrique.main.document.henrique_entity import HenriqueEntity, Entity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
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
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_prefix(cls):
        return re.compile(r"^\s*\?", re.I)

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        lang = LocaleTool.locale2lang(Entity.Config.config2locale(config))

        pattern_prefix = cls.pattern_prefix()
        match_list_prefix = list(pattern_prefix.finditer(text_in))

        span_value_list_skill = cls.lang2matcher(lang).text2span_value_list(text_in)

        spans_list = [lmap(lambda m:m.span(), match_list_prefix),
                      lmap(ig(0), span_value_list_skill)
                      ]
        gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)
        indextuple_list = ContextfreeTool.spans_list2reducible_indextuple_list(spans_list, gap2is_valid)

        def indextuple2entity(indextuple):
            index_prefix, index_skill = indextuple

            match_prefix = match_list_prefix[index_prefix]
            span_prefix = match_prefix.span()

            span_skill, value_skill = span_value_list_skill[index_skill]

            # span = (span_prefix[0], span_skill[1])

            entity = {Entity.Field.SPAN: span_skill,
                      Entity.Field.TEXT: StringTool.str_span2substr(text_in, span_skill),
                      Entity.Field.VALUE: value_skill,
                      Entity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(indextuple2entity, indextuple_list)
        return entity_list

    @classmethod
    def text2skill_code(cls, text):
        entity_list = cls.text2entity_list(text)
        entity = l_singleton2obj(entity_list)

        if entity is None:
            return None

        skill_code = Entity.entity2value(entity)
        return skill_code


WARMER.warmup()
