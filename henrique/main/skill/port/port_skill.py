import os
import re
import sys

from functools import lru_cache
from future.utils import lmap

from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.string.string_tool import str2split
from henrique.main.entity.khala_action import KhalaAction
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.tool.entity_tool import EntityTool
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

    @classmethod
    def j_skillnote2j_port_list(cls, j_note):
        return jdown(j_note, [SkillnoteTool.F.RESULT, PortResult.F.PORTS])

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "command.yaml")
        return YAMLTool.filepath2j(filepath)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_reversed(cls, ):
        return YAMLTool.j_yaml2h_reversed(cls.j_yaml())

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
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
    #     text = KhalaChat.j_chat2text(j_chat)
    #
    #     port_entity_list = PortEntity.str2entity_list(text)
    #
    #     str_list = lmap(lambda p:Port2PortSubaction.port_entity2response(p,j_packet), port_entity_list)
    #
    #     str_out = "\n\n".join(str_list)
    #
    #     return KhalaResponse.Builder.str2j_skillnote(str_out)

    @classmethod
    def str2j_skillnote(cls, str_in):
        port_entity_list = PortEntity.str2entity_list(str_in)

        j_port_list = lmap(EntityTool.entity2value, port_entity_list)
        j_result = {PortResult.F.PORTS: j_port_list}

        j_note = {SkillnoteTool.F.SPELL: str_in,
                  SkillnoteTool.F.RESULT: j_result,
                  }
        return j_note


WARMER.warmup()