import os
import sys
from itertools import chain

from foxylib.tools.collections.collections_tool import merge_dicts, luniq, IterTool
from functools import lru_cache
from nose.tools import assert_is_not_none

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class Server:
    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2server(cls):
        from henrique.main.entity.server.googlesheets.server_googlesheets import ServerGooglesheets
        server_list = ServerGooglesheets.server_list_all()
        assert_is_not_none(server_list)

        h_codename2server = merge_dicts([{cls.server2codename(server): server} for server in server_list])
        return h_codename2server

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def list_all(cls):
        return list(cls._dict_codename2server().values())

    @classmethod
    def server2codename(cls, server):
        return server[cls.Field.CODENAME]

    @classmethod
    def codename2server(cls, codename):
        return cls._dict_codename2server().get(codename)

    @classmethod
    def server_lang2aliases(cls, server, lang):
        return JsonTool.down(server, [cls.Field.ALIASES, lang]) or []

    @classmethod
    def server_langs2aliases(cls, server, langs):
        return luniq(chain(*[cls.server_lang2aliases(server, lang) for lang in langs]))

    @classmethod
    def server_lang2name(cls, server, lang):
        return IterTool.first(cls.server_lang2aliases(server, lang))

