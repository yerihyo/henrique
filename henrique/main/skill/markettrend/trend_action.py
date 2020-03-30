import os
import sys
from functools import lru_cache

from future.utils import lmap

from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.entity.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khalalib.packet.packet import KhalaPacket
from khalalib.response.khala_response import KhalaResponse

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

class TradegoodAction:


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "action.yaml")
        return YAMLTool.filepath2j(filepath)

    @classmethod
    def respond(cls, packet):
        from henrique.main.entity.tradegood.subaction.tradegood_subactions import TradegoodTradegoodSubaction

        text = KhalaPacket.packet2text(packet)
        
        tradegood_entity_list = TradegoodEntity.text2entity_list(text)

        str_list = lmap(lambda p:TradegoodTradegoodSubaction.tradegood_entity2response(p,packet), tradegood_entity_list)

        str_out = "\n\n".join(str_list)

        return KhalaResponse.Builder.str2j_response(str_out)

WARMER.warmup()