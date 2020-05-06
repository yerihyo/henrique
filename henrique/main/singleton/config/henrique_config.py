from functools import lru_cache

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.function.function_tool import FunctionTool


class HenriqueConfig:
    class Field:
        CHATROOM = "chatroom"
        SERVER = "server"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_chatroom2server(cls):
        from henrique.main.singleton.config.googlesheets.henrique_config_googlesheets import HenriqueConfigGooglesheets
        config_list = HenriqueConfigGooglesheets.config_list()

        h = merge_dicts([{config[cls.Field.CHATROOM]: config[cls.Field.SERVER]}
                         for config in config_list], vwrite=vwrite_no_duplicate_key)
        return h


    @classmethod
    def chatroom2server(cls, chatroom):
        return cls._dict_chatroom2server().get(chatroom)
