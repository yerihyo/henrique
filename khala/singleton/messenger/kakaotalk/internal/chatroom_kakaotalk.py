import logging
import sys

from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from khala.document.channel.channel import Channel
from khala.document.chatroom.chatroom import Chatroom
from khala.singleton.logger.khala_logger import KhalaLogger


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class ChatroomKakaotalk:
    class Constant:
        LOCALE = "ko-KR"
        NAME = "uwo"

    @classmethod
    def codename(cls):
        return Chatroom.Constant.DELIM.join([Channel.Codename.KAKAOTALK_UWO, cls.Constant.NAME])


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def chatroom(cls, ):
        logger = KhalaLogger.func_level2logger(cls.chatroom, logging.DEBUG)

        chatroom = {Chatroom.Field.CHANNEL: Channel.Codename.KAKAOTALK_UWO,
                    Chatroom.Field.CODENAME: cls.codename(),
                    # Chatroom.Field.EXTRA: ChatroomDiscord.Extra.message2extra(message),
                    Chatroom.Field.LOCALE: cls.Constant.LOCALE,
                    }
        logger.debug({"chatroom": chatroom,
                      })
        return chatroom

# WARMER.warmup()
