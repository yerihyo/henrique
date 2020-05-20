import re
from future.utils import lmap

from foxylib.tools.locale.locale_tool import LocaleTool

from foxylib.tools.cache.cache_tool import CacheTool
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.native.module.module_tool import ModuleTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2lower, StringTool, format_str
from henrique.main.document.henrique_entity import HenriqueEntity, Entity
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale

class Metricprefix:
    class Value:
        K = "k"
        M = "m"
        G = "g"

        @classmethod
        def set(cls):
            return {cls.K, cls.M, cls.G, }

    @classmethod
    def text2norm(cls, text):
        return str2lower(text)

    @classmethod
    def rstr(cls):
        return RegexTool.rstr_iter2or(map(re.escape,cls.Value.set()))

    @classmethod
    def text2multiple(cls, text):
        h = {cls.Value.K: 10 ** 3,
             cls.Value.M: 10 ** 6,
             cls.Value.G: 10 ** 9,
             }
        return h.get(cls.text2norm(text))


class RateEntity:
    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def text2norm(cls, text):
        return str2lower(text)

    @classmethod
    def rstr(cls):
        rstr = format_str(r"{}\s*{}?",
                          RegexTool.name_rstr2named("cardinal", "\d+", ),
                          RegexTool.name_rstr2named("Metricprefix", Metricprefix.rstr(),),
                          )
        return rstr

    @classmethod
    def match2value(cls, m):
        v = int(m.group("cardinal"))
        multiple = Metricprefix.text2multiple(m.group("Metricprefix")) or 1
        return v * multiple

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2pattern(cls, lang):
        from henrique.main.document.price.trend.trend_entity import TrendEntity

        rstr_suffix = format_str("{}?",
                                 RegexTool.rstr2wrapped(TrendEntity.lang2rstr(lang)),
                                 )

        ### may be concatenated with port/tradegood name
        # rstr_prefixed = RegexTool.rstr2rstr_words_prefixed(cls.rstr())
        # raise Exception({"rstr_suffix":rstr_suffix})
        rstr_suffixed = RegexTool.rstr2rstr_words_suffixed(cls.rstr(), rstr_suffix=rstr_suffix)

        # raise Exception({"rstr_trend": rstr_trend, "rstr_suffixed": rstr_suffixed})
        # return re.compile(RegexTool.rstr2rstr_words(cls.rstr()))
        return re.compile(rstr_suffixed, re.I)




    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        pattern = cls.lang2pattern(lang)
        m_list = list(pattern.finditer(text_in))

        def match2entity(m):
            span = m.span()
            entity = {Entity.Field.SPAN: span,
                      Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                      Entity.Field.VALUE: cls.match2value(m),
                      Entity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(match2entity, m_list)
        return entity_list


