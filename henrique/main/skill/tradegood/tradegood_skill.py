import os
import sys

from functools import partial, lru_cache
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap, merge_dicts, vwrite_no_duplicate_key
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.document.culture.culture_entity import CultureEntity
from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]


class TradegoodSkill:
    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.tradegood.tradegood_skill_description import TradegoodSkillDescription
        return TradegoodSkillDescription.lang2text(lang)

    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity}

    @classmethod
    def entity_lang2response_block(cls, entity, lang):
        entity_type = FoxylibEntity.entity2type(entity)
        codename = FoxylibEntity.entity2value(entity)

        from henrique.main.skill.tradegood.tradegood_port.tradegood_port_response import TradegoodPortResponse
        from henrique.main.skill.tradegood.tradegood_tradegood.tradegood_tradegood_response import TradegoodTradegoodResponse
        from henrique.main.skill.tradegood.tradegood_culture.tradegood_culture_response import TradegoodCultureResponse

        h_type2func = {PortEntity.entity_type(): partial(TradegoodPortResponse.codename_lang2text, lang=lang),
                       TradegoodEntity.entity_type(): partial(TradegoodTradegoodResponse.codename_lang2text, lang=lang),
                       CultureEntity.entity_type(): partial(TradegoodCultureResponse.codename_lang2text, lang=lang),
                       }

        assert_equals(set(h_type2func.keys()), smap(lambda c: c.entity_type(), cls.target_entity_classes()))

        codename2response = h_type2func.get(entity_type)
        if not codename2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        text_out = codename2response(codename)
        return Rowsblock.text2norm(text_out)


    @classmethod
    def packet2response(cls, packet):
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom)
        lang = LocaleTool.locale2lang(locale)

        entity_classes = cls.target_entity_classes()
        text_in = KhalaPacket.packet2text(packet)
        config = {HenriqueEntity.Config.Field.LOCALE: locale}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=FoxylibEntity.entity2span)

        response = Rowsblock.blocks2text([cls.entity_lang2response_block(entity, lang) for entity in entity_list])
        return response




