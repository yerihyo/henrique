import os
import sys

import re
from functools import lru_cache
from nose.tools import assert_in

from foxylib.tools.cache.cache_tool import CacheTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, lchain
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.native.module.module_tool import ModuleTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.span.span_tool import SpanTool
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.document.henrique_entity import Entity, HenriqueEntity
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class TradegoodEntitySpecialcase:

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_ko(cls):
        return re.compile(RegexTool.rstr2rstr_words(r"육메(?:크|클)?"))

    @classmethod
    def text2entity_list(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale)
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        if "ko" not in langs_recognizable:
            return []

        match_list = list(cls.pattern_ko().finditer(text_in))

        def match2entity_list(match):
            span = match.span()
            assert_in(SpanTool.span2len(span), (2, 3))
            entity_list = []

            s,e = span
            span_nutmeg = (s, s + 1)
            entity_nutmeg = {Entity.Field.SPAN: span_nutmeg,
                             Entity.Field.TEXT: StringTool.str_span2substr(text_in, span_nutmeg),
                             Entity.Field.VALUE: "Nutmeg",
                             Entity.Field.TYPE: TradegoodEntity.entity_type(),
                             }
            entity_list.append(entity_nutmeg)

            span_mace = (s + 1, s + 2)
            entity_mace = {Entity.Field.SPAN: span_mace,
                           Entity.Field.TEXT: StringTool.str_span2substr(text_in, span_mace),
                           Entity.Field.VALUE: "Mace",
                           Entity.Field.TYPE: TradegoodEntity.entity_type(),
                           }
            entity_list.append(entity_mace)

            if SpanTool.span2len(span) == 3:
                span_clove = (s + 2, s + 3)
                entity_cloves = {Entity.Field.SPAN: span_clove,
                               Entity.Field.TEXT: StringTool.str_span2substr(text_in, span_clove),
                               Entity.Field.VALUE: "Cloves",
                               Entity.Field.TYPE: TradegoodEntity.entity_type(),
                               }
                entity_list.append(entity_cloves)

            return entity_list

        entity_list = [entity
                       for m in match_list
                       for entity in match2entity_list(m)]
        return entity_list


class TradegoodEntity:
    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    def _dict_lang2matcher(cls,):
        return {lang: cls.lang2matcher(lang) for lang in HenriqueLocale.langs()}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        tg_list = Tradegood.list_all()
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        def tg2aliases(tg):
            for _lang in langs_recognizable:
                yield from Tradegood.tradegood_lang2aliases(tg, _lang)

        h_value2aliases = merge_dicts([{Tradegood.tradegood2codename(tg): list(tg2aliases(tg))} for tg in tg_list],
                                      vwrite=vwrite_no_duplicate_key)

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm,
                  GazetteerMatcher.Config.Key.TEXTS2PATTERN: HenriqueEntity.texts2rstr_word_with_cardinal_suffix,
                  }
        matcher = GazetteerMatcher(h_value2aliases, config)
        return matcher

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        entity_list_matcher = cls.text2entity_list_matcher(text_in, config=config)
        entity_list_specialcase = TradegoodEntitySpecialcase.text2entity_list(text_in, config=config)

        return lchain(entity_list_matcher, entity_list_specialcase)


    @classmethod
    def text2entity_list_matcher(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        matcher = cls.lang2matcher(lang)
        span_value_list = matcher.text2span_value_list(text_in)

        entity_list = [{Entity.Field.SPAN: span,
                        Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                        Entity.Field.VALUE: value,
                        Entity.Field.TYPE: cls.entity_type(),
                        }
                       for span, value in span_value_list]

        return entity_list




WARMER.warmup()


