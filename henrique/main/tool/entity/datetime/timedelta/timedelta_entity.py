import logging
import os
import sys
from operator import itemgetter as ig

import re
import yaml
from dateutil.relativedelta import relativedelta
from foxylib.tools.function.warmer import Warmer
from functools import lru_cache, partial
from future.utils import lmap
from nose.tools import assert_true

from foxylib.tools.collections.collections_tool import lchain, l_singleton2obj, ListTool
from foxylib.tools.entity.cardinal.cardinal_entity import CardinalEntity
from foxylib.tools.file.file_tool import FileTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.log.foxylib_logger import FoxylibLogger
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.native.native_tool import IntegerTool
from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import format_str, str2lower, StringTool
from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.abspath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class TimedeltaUnit:
    class Value:
        YEAR = "year"
        MONTH = "month"
        WEEK = "week"
        DAY = "day"
        HOUR = "hour"
        MINUTE = "minute"
        SECOND = "second"

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def yaml(cls):
        filepath = os.path.join(FILE_DIR, "timedelta_unit.yaml")
        j_yaml = YAMLTool.filepath2j(filepath, yaml.SafeLoader)
        return j_yaml

    @classmethod
    def normalize(cls, text):
        return str2lower(text)

    @classmethod
    def v_unit_lang2str(cls, v, unit, lang):
        j_yaml = cls.yaml()
        str_unit = JsonTool.down(j_yaml, [unit, lang])[0]

        if lang in {"en"}:
            return " ".join([str(v), str_unit])

        if lang in {"ko"}:
            return "".join([str(v), str_unit])

        raise Exception("Invalid language: {}".format(lang))


    @classmethod
    def unit2plural(cls, unit):
        return "{}s".format(unit)

    @classmethod
    def langs2matcher(cls, langs):
        return cls._langs2matcher(frozenset(langs))

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=4))
    def _langs2matcher(cls, langs):
        logger = HenriqueLogger.func_level2logger(cls._langs2matcher, logging.DEBUG)

        gazetteer = {k: lchain(*[j.get(lang, []) for lang in langs])
                     for k, j in cls.yaml().items()}

        def texts2pattern(texts):
            rstr = GazetteerMatcher.texts2regex_default(texts)
            logger.debug({"rstr":rstr})
            return re.compile(RegexTool.rstr2rstr_words_suffixed(rstr), re.I)

        config = {GazetteerMatcher.Config.Key.TEXTS2PATTERN: texts2pattern,
                  GazetteerMatcher.Config.Key.NORMALIZER: cls.normalize,
                  }
        matcher = GazetteerMatcher(gazetteer, config=config)
        return matcher

    @classmethod
    def warmer(cls):
        cls.langs2matcher({"ko", "en"})
        cls.langs2matcher({"en"})


class TimedeltaElement:
    class Field:
        QUANTITY = "quantity"
        UNIT = "unit"
        SPAN = "span"

    @classmethod
    def element2quantity(cls, element):
        return element[cls.Field.QUANTITY]

    @classmethod
    def element2unit(cls, element):
        return element[cls.Field.UNIT]

    @classmethod
    def element2span(cls, element):
        return element[cls.Field.SPAN]

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_number(cls):
        return re.compile(RegexTool.rstr2rstr_words_prefixed("\d+"))

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE))
    def text2element_list(cls, text_in, lang):
        logger = HenriqueLogger.func_level2logger(cls.text2element_list, logging.DEBUG)

        langs = HenriqueLocale.lang2langs_recognizable(lang)
        logger.debug({"langs":langs})

        match_list_number = list(cls.pattern_number().finditer(text_in))
        span_list_number = lmap(lambda m:m.span(), match_list_number)

        matcher = TimedeltaUnit.langs2matcher(langs)
        span_value_list_timedelta_unit = list(matcher.text2span_value_iter(text_in))

        spans_list = [span_list_number,
                      lmap(ig(0), span_value_list_timedelta_unit),
                      ]

        gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)
        indextuple_list = ContextfreeTool.spans_list2reducible_indextuple_list(spans_list, gap2is_valid)

        def indextuple2element(indextuple):
            i,j = indextuple

            quantity = int(match_list_number[i].group())
            unit = span_value_list_timedelta_unit[j][1]

            span = (span_list_number[i][0],
                    span_value_list_timedelta_unit[j][0][1],
                    )

            element = {cls.Field.QUANTITY: quantity,
                       cls.Field.UNIT: unit,
                       cls.Field.SPAN: span,
                       }

            return element

        element_list = lmap(indextuple2element, indextuple_list)
        return element_list

    @classmethod
    def element2relativedelta(cls, element):
        logger = HenriqueLogger.func_level2logger(cls.element2relativedelta, logging.DEBUG)

        unit = cls.element2unit(element)
        quantity = cls.element2quantity(element)
        kwargs = {TimedeltaUnit.unit2plural(unit): quantity}
        # logger.debug({"kwargs":kwargs})
        return relativedelta(**kwargs)


class TimedeltaEntity:
    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def text2entity_list(cls, text_in, config=None):
        locale = HenriqueEntity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        return cls._text2entity_list(text_in, lang)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE))
    def _text2entity_list(cls, text_in, lang):
        element_list = TimedeltaElement.text2element_list(text_in, lang)
        if not element_list:
            return []

        span_list_element = lmap(TimedeltaElement.element2span, element_list)

        def timedelta_list2indexes_group():
            gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)

            n = len(element_list)
            i_list_sorted = sorted(range(n), key=lambda i: span_list_element[i])

            indexes_continuous = [i_list_sorted[0]]
            for j in range(1, n):
                i_prev, i_this = i_list_sorted[j-1], i_list_sorted[j]

                span_gap = (span_list_element[i_prev][1],
                            span_list_element[i_this][0],
                            )
                if gap2is_valid(span_gap):
                    indexes_continuous.append(i_this)
                    continue

                yield indexes_continuous
                indexes_continuous = [i_this]

            yield indexes_continuous

        indexes_list = list(timedelta_list2indexes_group())

        def indexes2entity(indexes):
            span = (span_list_element[indexes[0]][0],
                    span_list_element[indexes[-1]][1],
                    )

            value = ListTool.indexes2filtered(element_list, indexes)

            entity = {FoxylibEntity.Field.SPAN: span,
                      FoxylibEntity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                      FoxylibEntity.Field.VALUE: value,
                      FoxylibEntity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(indexes2entity, indexes_list)
        return entity_list

    @classmethod
    def entity2relativedelta(cls, entity):
        logger = HenriqueLogger.func_level2logger(cls.entity2relativedelta, logging.DEBUG)

        element_list = FoxylibEntity.entity2value(entity)
        relativedelta_list = lmap(TimedeltaElement.element2relativedelta, element_list)
        logger.debug({"relativedelta_list":relativedelta_list})

        return sum(relativedelta_list, relativedelta(days=0))


class RelativeTimedeltaEntity:
    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    class Sign:
        class Constant:
            PLUS = "+"
            MINUS = "-"

        @classmethod
        @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
        @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
        def pattern(cls):
            return re.compile(RegexTool.rstr2rstr_words("[+-]"))

        @classmethod
        def sign2int(cls, sign):
            h = {cls.Constant.PLUS: 1, cls.Constant.MINUS: -1}
            return h[sign]

    class Value:
        class Field:
            SIGN = "sign"
            TIMEDELTA = "timedelta"

        @classmethod
        def value2sign(cls, value):
            return value[cls.Field.SIGN]

        @classmethod
        def value2timedelta(cls, value):
            return value[cls.Field.TIMEDELTA]

        @classmethod
        def value2relativedelta(cls, value):
            logger = FoxylibLogger.func_level2logger(cls.value2relativedelta, logging.DEBUG)

            sign = cls.value2sign(value)
            int_sign = RelativeTimedeltaEntity.Sign.sign2int(sign)

            timedelta_entity = cls.value2timedelta(value)
            return int_sign * TimedeltaEntity.entity2relativedelta(timedelta_entity)

    @classmethod
    def text2entity_list(cls, text_in, config=None):
        locale = HenriqueEntity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        return cls._text2entity_list(text_in, lang)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE))
    def _text2entity_list(cls, text_in, lang):
        match_list_sign = list(cls.Sign.pattern().finditer(text_in))
        span_list_sign = lmap(lambda m: m.span(), match_list_sign)

        entity_list_timedelta = TimedeltaEntity._text2entity_list(text_in, lang)
        span_list_timedelta = lmap(FoxylibEntity.entity2span, entity_list_timedelta)

        span_lists = [span_list_sign, span_list_timedelta,]
        gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)
        indextuple_list = ContextfreeTool.spans_list2reducible_indextuple_list(span_lists, gap2is_valid)

        def indextuple2entity(indextuple):
            i, j = indextuple

            match_sign = match_list_sign[i]
            span_sign = span_list_sign[i]
            sign = match_sign.group()

            entity_timedelta = entity_list_timedelta[j]
            span_timedelta = span_list_timedelta[j]

            value = {cls.Value.Field.SIGN: sign,
                     cls.Value.Field.TIMEDELTA: entity_timedelta
                     }

            span = (span_sign[0],
                    span_timedelta[1],
                    )
            entity = {FoxylibEntity.Field.SPAN: span,
                      FoxylibEntity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                      FoxylibEntity.Field.VALUE: value,
                      FoxylibEntity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(indextuple2entity, indextuple_list)
        return entity_list

    @classmethod
    def entity2relativedelta(cls, entity):
        return cls.Value.value2relativedelta(FoxylibEntity.entity2value(entity))


WARMER.warmup()
