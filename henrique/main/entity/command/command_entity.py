import os
from operator import itemgetter as ig

import re
from future.utils import lmap

from foxylib.tools.nlp.contextfree.contextfree_tool import ContextfreeTool

from foxylib.tools.entity.entity_tool import Entity

from functools import lru_cache, partial

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.skill.henrique_skill import HenriqueSkill

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class CommandEntity:
    @classmethod
    def set(cls):
        from henrique.main.skill.port.port_skill import PortSkill
        return {PortSkill,
                }

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_name2skill(cls):
        return merge_dicts([{skill.NAME: skill}
                            for skill in cls.set()],
                           vwrite=vwrite_no_duplicate_key)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_prefix(cls):
        return re.compile(r"^\s*\?", re.I)

    @classmethod
    def text2entity_list(cls, text_in):
        pattern_prefix = cls.pattern_prefix()
        match_list_prefix = list(pattern_prefix.finditer(text_in))

        span_value_list_skill = HenriqueSkill.matcher().text2span_value_list(text_in)

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

            span = (span_prefix[0], span_skill[1])

            entity = {Entity.Field.SPAN: span,
                      Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                      Entity.Field.VALUE: value_skill,
                      }
            return entity

        entity_list = lmap(indextuple2entity, indextuple_list)
        return entity_list
