import os
import sys

import re
from functools import lru_cache, partial

from foxylib.tools.collections.collections_tool import lchain
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.regex.regex_tool import RegexTool
from henrique.main.entity.henrique_entity import Entity
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.tool.skillnote_tool import SkillnoteTool
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class PortResult:
    class Field:
        PORTS = "ports"
    F = Field

class PortSkill:
    CODENAME = "port"

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
    def _entity_lang2response(cls, entity, lang):
        entity_type = Entity.entity2type(entity)
        codename = Entity.entity2value(entity)

        from henrique.main.skill.port.port_port.port_port_response import PortPortResponse
        h_type2func = {PortEntity.TYPE: partial(PortPortResponse.codename_lang2response, lang=lang),
                       }

        codename2response = h_type2func.get(entity_type)
        if not codename2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        return codename2response(codename)


    @classmethod
    def packet2response(cls, packet):
        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(packet))

        entity_classes = {PortEntity}
        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE:KhalaPacket.packet2locale(packet)}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=Entity.entity2span)

        response = "\n\n".join([cls._entity_lang2response(entity, lang) for entity in entity_list])
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