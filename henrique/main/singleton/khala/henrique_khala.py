import re
import sys

from nose.tools import assert_in

from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool
from functools import lru_cache, partial

from future.utils import lfilter, lmap

from foxylib.tools.collections.collections_tool import l_singleton2obj
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.string.string_tool import str2strip, StringTool
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.skill.skill_entity import SkillEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khala.document.packet.packet import KhalaPacket

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class HenriqueKhala:
    @classmethod
    def packet2response(cls, packet):
        from henrique.main.document.skill.skill_entity import HenriqueSkill

        skill_code = HenriqueCommand.packet2skill_code(packet)
        skill_class = HenriqueSkill.codename2class(skill_code)
        response_raw = skill_class.packet2response(packet)
        return Rowsblock.text2norm(response_raw)


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

        entity_list = SkillEntity.text2entity_list(text_in, config=config)

        pattern_prefix = cls.pattern_prefix()
        match_list_prefix = list(pattern_prefix.finditer(text_in))

        spans_list = [lmap(lambda m: m.span(), match_list_prefix),
                      lmap(Entity.entity2span, entity_list)
                      ]
        gap2is_valid = partial(StringTool.str_span2match_blank_or_nullstr, text_in)
        indextuple_list = ContextfreeTool.spans_list2reducible_indextuple_list(spans_list, gap2is_valid)

        assert_in(len(indextuple_list), [0, 1])

        if not indextuple_list:
            return None

        entity = l_singleton2obj(indextuple_list)[1]
        return SkillEntity.entity2skill_codename(entity)


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

WARMER.warmup()