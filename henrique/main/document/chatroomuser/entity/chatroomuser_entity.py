import os
import re

import yaml
from future.utils import lmap
from nose.tools import assert_equal

from foxylib.tools.cache.cache_tool import CacheTool
from functools import lru_cache

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, lchain
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.native.clazz.class_tool import ClassTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from khala.document.chatroom.chatroom import Chatroom, KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class Me:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "me.yaml")
        j_yaml = YAMLTool.filepath2j(filepath, Loader=yaml.SafeLoader)
        return j_yaml

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2pattern(cls, lang):
        j_me = cls.j_yaml()

        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)
        me_list = [me
                   for lang in langs_recognizable
                   for me in j_me.get(lang, [])]
        rstr = RegexTool.rstr_iter2or(map(re.escape, me_list))
        pattern = re.compile(rstr, re.I)
        return pattern


class ChatroomuserEntity:
    class Constant:
        ME = Me

    @classmethod
    def entity_type(cls):
        return ClassTool.class2fullpath(cls)

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def matcher_names(cls):
        h_codename2aliases = merge_dicts([{Chatroomuser.chatroomuser2codename(chatroomuser): Chatroomuser.chatroomuser2aliases(chatroomuser)}
                                          for chatroomuser in Chatroomuser.list_all()],
                                         vwrite=vwrite_no_duplicate_key)

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm,
                  # GazetteerMatcher.Config.Key.TEXTS2PATTERN: HenriqueEntity.texts2rstr_word_with_cardinal_suffix,
                  }
        matcher = GazetteerMatcher(h_codename2aliases, config)
        return matcher

    @classmethod
    def text2entity_list(cls, text_in, config=None):
        locale = HenriqueEntity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        return cls._text2entity_list(text_in, lang)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE))
    def _text2entity_list(cls, text_in, lang):
        return lchain(cls._text2entity_list_me(text_in, lang),
                      cls._text2entity_list_names(text_in, ),
                      )

    @classmethod
    def _text2entity_list_names(cls, text_in):

        matcher_names = cls.matcher_names()
        span_value_list = list(matcher_names.text2span_value_iter(text_in),)

        entity_list = [{FoxylibEntity.Field.SPAN: span,
                        FoxylibEntity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                        FoxylibEntity.Field.VALUE: value,
                        FoxylibEntity.Field.TYPE: cls.entity_type(),
                        }
                       for span, value in span_value_list]

        return entity_list

    @classmethod
    def _text2entity_list_me(cls, text_in, lang):
        p = Me.lang2pattern(lang)
        m_list = list(p.finditer(text_in))

        def match2entity(m):
            span = m.span()
            entity = {FoxylibEntity.Field.SPAN: span,
                      FoxylibEntity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                      FoxylibEntity.Field.VALUE: cls.Constant.ME,
                      FoxylibEntity.Field.TYPE: cls.entity_type(),
                      }
            return entity

        entity_list = lmap(match2entity, m_list)
        return entity_list

    @classmethod
    def entity2is_me(cls, entity):
        value = FoxylibEntity.entity2value(entity)
        return value == cls.Constant.ME

    @classmethod
    def value_packet2codename(cls, value, packet):
        if value != cls.Constant.ME:
            return value

        assert_equal(KhalaPacket.packet2chatroom(packet), KakaotalkUWOChatroom.codename())

        sender_name = KhalaPacket.packet2sender_name(packet)
        return sender_name


