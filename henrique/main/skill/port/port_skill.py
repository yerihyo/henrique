import os
import sys

import re
from functools import lru_cache, partial
from khalalib.packet.packet import KhalaPacket

from foxylib.tools.entity.entity_tool import Entity
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2split
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.tool.skillnote_tool import SkillnoteTool

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class PortResult:
    class Field:
        PORTS = "ports"
    F = Field

class PortSkill:
    NAME = "port"

    @classmethod
    def j_skillnote2j_port_list(cls, j_note):
        return jdown(j_note, [SkillnoteTool.F.RESULT, PortResult.F.PORTS])

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "command.yaml")
        return YAMLTool.filepath2j(filepath)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_reversed(cls, ):
        return YAMLTool.j_yaml2h_reversed(cls.j_yaml())

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def p_command(cls, ):
        rstr = RegexTool.rstr_list2or(list(cls.h_reversed().keys()))
        p = re.compile(rstr, re.I)
        return p

    @classmethod
    def text_body2match(cls, text_body):
        l = str2split(text_body)
        m = cls.p_command().match(l[0])
        return m

    # @classmethod
    # def respond(cls, j_packet):
    #
    #
    #     j_chat = KhalaPacket.j_packet2j_chat(j_packet)
    #     text = KhalaPacket.chat2text(j_chat)
    #
    #     port_entity_list = PortEntity.text2entity_list(text)
    #
    #     str_list = lmap(lambda p:Port2PortSubaction.port_entity2response(p,j_packet), port_entity_list)
    #
    #     str_out = "\n\n".join(str_list)
    #
    #     return KhalaResponse.Builder.str2j_skillnote(str_out)

    @classmethod
    def _entity2response(cls, entity, lang):
        entity_type = Entity.entity2type(entity)

        from henrique.main.skill.port.port_entity.port_skill_port_entity import PortSkillPortEntity
        h = {PortEntity.TYPE: partial(PortSkillPortEntity.code2response, lang=lang),
             }

        code2response = h.get(entity_type)
        if not code2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        value = Entity.entity2value(entity)
        return code2response(value)


    @classmethod
    def anatomy2response(cls, anatomy):
        entity_types = {PortEntity.TYPE}
        entity_list = sorted(anatomy.entity_types2entity_list(entity_types), key=Entity.entity2span)

        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(anatomy.packet))
        response = "\n\n".join([cls._entity2response(entity, lang) for entity in entity_list])
        return response



    # @classmethod
    # def str2j_skillnote(cls, str_in):
    #     port_entity_list = PortEntity.text2entity_list(str_in)
    #
    #     j_port_list = lmap(Entity.entity2value, port_entity_list)
    #     j_result = {PortResult.F.PORTS: j_port_list}
    #
    #     j_note = {SkillnoteTool.F.SPELL: text_in,
    #               SkillnoteTool.F.RESULT: j_result,
    #               }
    #     return j_note





WARMER.warmup()