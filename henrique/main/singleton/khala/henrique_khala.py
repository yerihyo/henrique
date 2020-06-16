import sys

import re
from foxylib.tools.cache.cache_tool import CacheTool
from functools import lru_cache, partial
from future.utils import lfilter, lmap
from nose.tools import assert_in

from foxylib.tools.collections.collections_tool import l_singleton2obj
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool
from foxylib.tools.string.string_tool import str2strip, StringTool
from henrique.main.document.henrique_entity import Entity, HenriqueEntity
from henrique.main.document.skill.skill_entity import SkillEntity
from henrique.main.singleton.config.henrique_config import HenriqueConfig
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.error.henrique_error import ErrorhandlerKakaotalk
from khala.document.packet.packet import KhalaPacket

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class HenriquePacket:
    @classmethod
    @ErrorhandlerKakaotalk.decorator_unknown_error_handler
    def packet2response(cls, packet):
        from henrique.main.document.skill.skill_entity import HenriqueSkill

        skill_code = HenriqueCommand.packet2skill_code(packet)
        if not skill_code:
            return None

        skill_class = HenriqueSkill.codename2class(skill_code)
        response_raw = skill_class.packet2response(packet)
        return Rowsblock.text2norm(response_raw)

    @classmethod
    def packet2server(cls, packet):
        chatroom_codename = KhalaPacket.packet2chatroom(packet)
        server_codename = HenriqueConfig.chatroom2server(chatroom_codename)
        if not server_codename:
            raise RuntimeError("Chatroom without config: {}".format(chatroom_codename))

        return server_codename


class HenriqueCommand:
    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_prefix(cls):
        return re.compile(r"^\s*\?", re.I)

    @classmethod
    def packet2skill_code(cls, packet):
        text_in = KhalaPacket.packet2text(packet)
        config = Entity.Config.packet2config(packet)
        return cls._text_config2skill_code(text_in, config)

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def _text_config2skill_code(cls, text_in, config):
        pattern_prefix = cls.pattern_prefix()
        match_list_prefix = list(pattern_prefix.finditer(text_in))
        if not match_list_prefix:
            return None

        entity_list = SkillEntity.text2entity_list(text_in, config=config)
        if not entity_list:
            return None

        spans_list = [lmap(lambda m: m.span(), match_list_prefix),
                      lmap(Entity.entity2span, entity_list)
                      ]
        gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)
        indextuple_list = ContextfreeTool.spans_list2reducible_indextuple_list(spans_list, gap2is_valid)

        assert_in(len(indextuple_list), [0, 1])

        if not indextuple_list:
            return None

        index_entity = l_singleton2obj(indextuple_list)[1]
        entity = entity_list[index_entity]
        return SkillEntity.entity2skill_codename(entity)

    @classmethod
    def text2is_query(cls, text):
        return bool(cls.pattern_prefix().match(text))



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

# WARMER.warmup()