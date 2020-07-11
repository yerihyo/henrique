import re

from itertools import chain
from nose.tools import assert_greater_equal

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, lchain
from functools import lru_cache, partial

from foxylib.tools.entity.entity_tool import FoxylibEntity
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.span.span_tool import SpanTool
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

class HenriqueEntity:
    class Cache:
        DEFAULT_SIZE = 100

    class Config:
        # class Step:
        #     PRECISION = "precision"
        #     RECALL = "recall"

        class Field:
            LOCALE = "locale"
            # STEP = "step"

        @classmethod
        def config2locale(cls, j):
            if not j:
                return None

            return j.get(cls.Field.LOCALE)

        @classmethod
        def packet2config(cls, packet):
            chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
            locale = Chatroom.chatroom2locale(chatroom)

            config = {cls.Field.LOCALE: locale,
                      # cls.Field.STEP: cls.Step.PRECISION,
                      }
            return config

    @classmethod
    def entity2key(cls, entity):
        s, e = FoxylibEntity.entity2span(entity)

        k = (s,
             -e,
             FoxylibEntity.entity2type(entity),
             FoxylibEntity.entity2value(entity),
             FoxylibEntity.entity2text(entity),
             )
        return k

    @classmethod
    def text_classes2entity_list(cls, text_in, entity_classes, config):
        extractor_list = [partial(c.text2entity_list, config=config) for c in entity_classes]
        entity_list = cls.text_extractors2entity_list(text_in, extractor_list,)
        return entity_list

    @classmethod
    def entity_list2inferior_excluded(cls, entity_list_in):
        entity_list = sorted(entity_list_in, key=cls.entity2key)

        def entities2valid(entities):
            span_furthest = None

            for entity in entities:
                span = FoxylibEntity.entity2span(entity)

                if span_furthest and SpanTool.covers_strictly(span_furthest, span):
                    continue

                if (span_furthest is None) or span_furthest[1] < span[1]:
                    span_furthest = span

                yield entity

        return list(entities2valid(entity_list))

    @classmethod
    def text_extractors2entity_list(cls, text_in, extractors):
        entity_ll = [f(text_in) for f in extractors]
        entity_list_raw = lchain(*entity_ll)
        entity_list_filtered = cls.entity_list2inferior_excluded(entity_list_raw)
        entity_list = sorted(entity_list_filtered, key=cls.entity2key)
        return entity_list

    # @classmethod
    # def texts2rstr_word_with_cardinal_suffix(cls, texts):
    #     regex_raw = RegexTool.rstr_iter2or(map(re.escape, texts))
    #     rstr_prefixed = RegexTool.rstr2left_bounded(regex_raw, RegexTool.left_wordbounds())
    #
    #     rstr_suf = r"(?=(?:\s|\b|[0-9]|$))"
    #     rstr_word = r'{0}{1}'.format(RegexTool.rstr2wrapped(rstr_prefixed), rstr_suf)
    #
    #     return re.compile(rstr_word, )  # re.I can be dealt with normalizer

    def texts2pattern_port_tradegood(cls, texts):
        left_bounds = RegexTool.left_wordbounds()
        right_bounds = lchain(RegexTool.right_wordbounds(), ["\d+"],)
        rstr_bounded = RegexTool.rstr2bounded(RegexTool.rstr_iter2or(map(re.escape, texts)), left_bounds, right_bounds,)
        return re.compile(rstr_bounded)
        # regex_raw = RegexTool.rstr_iter2or(map(re.escape, texts))
        # rstr_prefixed = RegexTool.rstr2rstr_words_prefixed(regex_raw)
        #
        # rstr_suf = r"(?=(?:\s|\b|[0-9]|$))"
        # rstr_word = r'{0}{1}'.format(RegexTool.rstr2wrapped(rstr_prefixed), rstr_suf)

        # return re.compile(rstr_bounded, )  # re.I can be dealt with normalizer

    # @classmethod
    # def classes(cls):
    #     from henrique.main.document.port.port_entity import PortEntity
    #
    #     from henrique.main.document.skill.skill_entity import SkillEntity
    #     from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
    #     from henrique.main.document.markettrend.trend_entity import MarkettrendEntity
    #
    #     h = {SkillEntity,
    #          PortEntity,
    #          TradegoodEntity,
    #          MarkettrendEntity,
    #          }
    #     return h
    #
    # @classmethod
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def _h_type2class(cls):
    #     h = merge_dicts([{clazz.TYPE: clazz} for clazz in cls.classes()],
    #                     vwrite=vwrite_no_duplicate_key)
    #     return h
    #
    # @classmethod
    # def entity_type2class(cls, entity_type):
    #     h = cls._h_type2class()
    #     return h.get(entity_type)

    # @classmethod
    # def text_entity_class2entity_list(cls, text, entity_class):
    #     return entity_class.text2entity_list(text)

