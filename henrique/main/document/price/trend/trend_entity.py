import re

from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.native.module.module_tool import ModuleTool
from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_overwrite, DictTool, vwrite_no_duplicate_key
from future.utils import lfilter, lmap

from foxylib.tools.cache.cache_tool import CacheTool

from foxylib.tools.locale.locale_tool import LocaleTool

from functools import lru_cache, partial
from nose.tools import assert_is_not_none

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2lower, StringTool, format_str
from henrique.main.document.henrique_entity import Entity, HenriqueEntity
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale


class Trend:
    class Value:
        SKYRISE = "skyrise"
        RISE = "rise"
        AVERAGE = "average"
        DOWN = "down"
        PLUMMET = "plummet"

        @classmethod
        def list(cls):
            return [cls.PLUMMET, cls.DOWN, cls.AVERAGE, cls.RISE, cls.SKYRISE]

    @classmethod
    def trend_int_list(cls):
        return [(cls.Value.SKYRISE, 2,),
                (cls.Value.RISE, 1,),
                (cls.Value.AVERAGE, 0,),
                (cls.Value.DOWN, -1,),
                (cls.Value.PLUMMET, -2,),
                ]

    @classmethod
    def int2trend(cls, num):
        for v, i in cls.trend_int_list():
            if num == i:
                return v

        raise RuntimeError({"num":num})

    @classmethod
    def trend2int(cls, trend):
        for v, i in cls.trend_int_list():
            if trend == v:
                return i

        raise RuntimeError({"trend":trend})

    @classmethod
    def dict_trend2arrow(cls,):
        h = {cls.Value.SKYRISE: '↑',
             cls.Value.RISE: '↗',
             cls.Value.AVERAGE: '→',
             cls.Value.DOWN: '↘',
             cls.Value.PLUMMET: '↓',
             }
        return h

    @classmethod
    def trend2arrow(cls, trend):
        arrow = cls.dict_trend2arrow().get(trend)
        assert_is_not_none(arrow)
        return arrow


class TrendEntity:
    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_lang2codename2texts(cls):
        from henrique.main.document.price.trend.googlesheets.trend_googlesheets import TrendGooglesheets
        h = TrendGooglesheets.dict_lang2codename2texts()
        return h

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def _lang2dict_alias2codename(cls, lang):

        langs = HenriqueLocale.lang2langs_recognizable(lang)
        h = cls.dict_lang2codename2texts()
        # h_codename2aliases = cls.dict_lang2codename2texts().get(lang)

        h_alias2codename = merge_dicts([{cls.text2norm(alias): codename}
                                        for lang in langs
                                        for codename, aliases in h.get(lang).items()
                                        for alias in aliases],
                                       vwrite=vwrite_no_duplicate_key)
        return h_alias2codename

    @classmethod
    def lang_alias2codename(cls, lang, alias):
        h_alias2codename = cls._lang2dict_alias2codename(lang)
        return h_alias2codename.get(alias)

    @classmethod
    def lang2rstr(cls, lang):
        aliases = cls._lang2dict_alias2codename(lang).keys()
        return RegexTool.rstr_iter2or(map(lambda x: re.escape(cls.text2norm(x)), aliases))

    @classmethod
    def lang2pattern(cls, lang):
        from henrique.main.document.price.rate.rate_entity import RateEntity
        rstr = format_str(r"{}\s*{}",
                          RegexTool.rstr2wrapped(RateEntity.rstr()),
                          RegexTool.name_rstr2named("trend", cls.lang2rstr(lang),)
                          )
        rstr_right_bounded = RegexTool.rstr2right_bounded(rstr, RegexTool.right_wordbounds())
        return re.compile(rstr_right_bounded, re.I)

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale)

        pattern = cls.lang2pattern(lang)

        m_list = list(pattern.finditer(text_in))

        def match2entity(match):
            span = match.span("trend")
            text = StringTool.str_span2substr(text_in, span)
            codename = cls.lang_alias2codename(lang, text)

            entity = {Entity.Field.VALUE: codename,
                      Entity.Field.TEXT: text,
                      Entity.Field.SPAN: span,
                      Entity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(match2entity, m_list)
        return entity_list




