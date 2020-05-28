import os

from functools import lru_cache, partial
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap, vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class ErrorSkill:
    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.port.port_skill_description import PortSkillDescription
        return PortSkillDescription.lang2text(lang)

    @classmethod
    def packet2response(cls, packet):
        text_in = KhalaPacket.packet2text(packet)
        raise RuntimeError({"skill":"?error","text_in":text_in,})



