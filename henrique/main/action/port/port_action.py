import os
import sys

from functools import lru_cache
from future.utils import lmap

from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.string.string_tool import str2split
from henrique.main.entity.entity import Entity
from henrique.main.entity.khala_action import KhalaAction
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.hub.env.henrique_env import HenriqueEnv

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class PortAnswer:
    class Field:
        SPELL = "spell"
        PORTS = "ports"
    F = Field

    @classmethod
    def j_answer2spell(cls, j_answer):
        return j_answer[cls.F.SPELL]

    @classmethod
    def j_answer2j_port_list(cls, j_answer):
        return j_answer[cls.F.PORTS]

class PortSpell:
    @classmethod
    @WARMER.add(cond=EnvTool.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "command.yaml")
        return YAMLTool.filepath2j(filepath)

    @classmethod
    @WARMER.add(cond=EnvTool.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def p_command(cls, ):
        return KhalaAction.j_yaml2p_command(cls.j_yaml())

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
    #     return KhalaResponse.Builder.str2j_answer(str_out)

    @classmethod
    def str2j_answer(cls, str_in):
        port_entity_list = PortEntity.str2entity_list(str_in)

        j_port_list = lmap(Entity.entity2value, port_entity_list)
        j_answer = {PortAnswer.F.SPELL: str_in,
                      PortAnswer.F.PORTS: j_port_list,
                      }
        return j_answer


WARMER.warmup()