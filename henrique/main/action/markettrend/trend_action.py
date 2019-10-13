import os
import sys
from functools import lru_cache

from future.utils import lmap

from foxylib.tools.env.env_tools import EnvToolkit
from foxylib.tools.function.function_tools import FunctionToolkit
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.yaml_tools import YAMLToolkit
from henrique.main.action.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.hub.env.henrique_env import HenriqueEnv
from khalalib.chat.chat import KhalaChat
from khalalib.packet.packet import KhalaPacket
from khalalib.response.khala_response import KhalaResponse

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class TradegoodAction:


    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "action.yaml")
        return YAMLToolkit.filepath2j(filepath)

    @classmethod
    def respond(cls, j_packet):
        from henrique.main.action.tradegood.subaction.tradegood_subactions import TradegoodTradegoodSubaction

        j_chat = KhalaPacket.j_packet2j_chat(j_packet)
        text = KhalaChat.j_chat2text(j_chat)
        
        tradegood_entity_list = TradegoodEntity.str2entity_list(text)

        str_list = lmap(lambda p:TradegoodTradegoodSubaction.tradegood_entity2response(p,j_packet), tradegood_entity_list)

        str_out = "\n\n".join(str_list)

        return KhalaResponse.Builder.str2j_response(str_out)

WARMER.warmup()