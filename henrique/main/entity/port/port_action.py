import os
import re
import sys
from functools import lru_cache

from future.utils import lmap

from foxylib.tools.collections.collections_tools import lchain
from foxylib.tools.env.env_tools import EnvToolkit
from foxylib.tools.function.function_tools import FunctionToolkit
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.yaml_tools import YAMLToolkit
from foxylib.tools.regex.regex_tools import RegexToolkit
from foxylib.tools.string.string_tools import str2split
from henrique.main.entity.khala_action import KhalaAction
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.hub.env.henrique_env import HenriqueEnv
from khalalib.chat.chat import KhalaChat
from khalalib.packet.packet import KhalaPacket
from khalalib.response.khala_response import KhalaResponse

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class PortAction:


    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "action.yaml")
        return YAMLToolkit.filepath2j(filepath)

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def p_command(cls, ):
        return KhalaAction.j_yaml2p_command(cls.j_yaml())

    @classmethod
    def text_body2match(cls, text_body):
        l = str2split(text_body)
        m = cls.p_command().match(l[0])
        return m

    @classmethod
    def respond(cls, j_packet):
        from henrique.main.entity.port.subaction.port_subactions import PortPortSubaction

        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = KhalaChat.j_chat2text(j_chat)
        
        port_entity_list = PortEntity.str2entity_list(text)

        str_list = lmap(lambda p:PortPortSubaction.port_entity2response(p,j_packet), port_entity_list)

        str_out = "\n\n".join(str_list)

        return KhalaResponse.Builder.str2j_response(str_out)

WARMER.warmup()