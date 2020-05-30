import os
import sys

from functools import lru_cache
from itertools import chain

from foxylib.tools.collections.collections_tool import merge_dicts, luniq, DictTool
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class Chatroomuser:
    class Field:
        CODENAME = "codename"
        COMMENTS = "comments"
        ALIASES = "aliases"

    @classmethod
    def _dict_codename2chatroomuser_all(cls):
        from henrique.main.document.chatroomuser.googlesheets.chatroomuser_googlesheets import ChatroomuserGooglesheets
        return ChatroomuserGooglesheets.dict_codename2chatroomuser()


    @classmethod
    def list_all(cls):
        return list(cls._dict_codename2chatroomuser_all().values())

    @classmethod
    def chatroomuser2codename(cls, chatroomuser):
        return chatroomuser[cls.Field.CODENAME]

    @classmethod
    def chatroomuser2comments(cls, chatroomuser):
        return chatroomuser.get(cls.Field.COMMENTS) or []

    @classmethod
    def chatroomuser2aliases(cls, chatroomuser):
        return chatroomuser.get(cls.Field.ALIASES) or [cls.chatroomuser2codename(chatroomuser)]

    @classmethod
    def codename2chatroomuser(cls, codename):
        chatroomuser = cls._dict_codename2chatroomuser_all().get(codename)
        if chatroomuser:
            return chatroomuser

        return {cls.Field.CODENAME: codename,}


WARMER.warmup()
