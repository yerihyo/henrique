import logging
import os

from functools import lru_cache
from itertools import chain
from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, luniq, vwrite_no_duplicate_key
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.singleton.config.henrique_config import HenriqueConfig
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class Server:
    class Codename:
        MARIS = "maris"
        HELENE = "helene"
        EIRENE = "eirene"
        POLARIS = "polaris"
        JAPAN = "japan"

        @classmethod
        def set(cls):
            return {cls.MARIS, cls.HELENE, cls.EIRENE, cls.POLARIS}

    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _lang2dict_alias2server(cls, lang):
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)
        h = merge_dicts([{alias: server}
                         for server in cls.list_all()
                         for alias in cls.server_langs2aliases(server, langs_recognizable)],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def alias_lang2server(cls, alias, lang):
        logger = HenriqueLogger.func_level2logger(cls.alias_lang2server, logging.DEBUG)

        h = cls._lang2dict_alias2server(lang)
        # logger.debug({"h": h})
        return h.get(alias)


    @classmethod
    def packet2codename(cls, packet):
        chatroom_codename = KhalaPacket.packet2chatroom(packet)
        server_codename = HenriqueConfig.chatroom2server(chatroom_codename)
        if not server_codename:
            raise RuntimeError("Chatroom without config: {}".format(chatroom_codename))

        return server_codename

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2server(cls):
        from henrique.main.document.server.googlesheets.server_googlesheets import ServerGooglesheets
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


