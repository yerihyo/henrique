import os

from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from functools import lru_cache

from future.utils import lmap

from foxylib.tools.collections.collections_tool import luniq
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.skill.skill_entity import SkillEntity, HenriqueSkill
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class HelpSkill:
    class Sheetname:
        PRICE = "price"
        PORT = "port"
        TRADEGOOD = "tradegood"
        CULTURE = "culture"
        HELP = "help"

        @classmethod
        def list(cls):
            return [cls.PRICE, cls.PORT, cls.TRADEGOOD, cls.CULTURE, cls.HELP]

    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.help.help_skill_description import HelpSkillDescription
        return HelpSkillDescription.lang2text(lang)

    @classmethod
    def target_entity_classes(cls):
        return {SkillEntity, }

    @classmethod
    def spreadsheet_id(cls):
        return "1dU_Wbx4Y0ov5QjXGS4gjNAsXewFlq1R-__ewvVZ_TTE"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_sheetname2data_ll(cls, ):
        sheetname_list = cls.Sheetname.list()
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheet_id(),
                                                                sheetname_list,
                                                                )

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    def packet2response(cls, packet):
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom)
        lang = LocaleTool.locale2lang(locale)

        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE: locale}
        entity_list_skill = SkillEntity.text2entity_list(text_in, config=config)

        codename_list = luniq(map(SkillEntity.entity2skill_codename, entity_list_skill))
        clazz_list = lmap(HenriqueSkill.codename2class, codename_list)

        blocks = [clazz.lang2help_response_block(lang) for clazz in clazz_list]
        return Rowsblock.blocks2text(blocks)

