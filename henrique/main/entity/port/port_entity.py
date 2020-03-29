import os
import sys

from functools import lru_cache

from foxylib.tools.cache.cache_tool import CacheTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.entity.henrique_entity import Entity, HenriqueEntity
from henrique.main.entity.port.port import Port
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class PortEntity:
    TYPE = "port"

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    # @classmethod
    # @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    # def _dict_lang2matcher(cls,):
    #     return {lang: cls.lang2matcher(lang) for lang in HenriqueLocale.langs()}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        def port2aliases(port):
            for _lang in langs_recognizable:
                yield from Port.port_lang2aliases(port, _lang)

        h_codename2aliases = merge_dicts([{Port.port2codename(port): list(port2aliases(port))}
                                          for port in Port.lis_all()],
                                         vwrite=vwrite_no_duplicate_key)

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm}
        matcher = GazetteerMatcher(h_codename2aliases, config)
        return matcher

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        matcher = cls.lang2matcher(lang)
        span_value_list = matcher.text2span_value_list(text_in)

        entity_list = [{Entity.Field.SPAN: span,
                        Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                        Entity.Field.VALUE: value,
                        Entity.Field.TYPE: cls.TYPE,
                        }
                       for span, value in span_value_list]

        return entity_list








WARMER.warmup()


