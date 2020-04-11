import os
import sys

import re
from functools import lru_cache, partial
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.regex.regex_tool import RegexTool
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.skill.henrique_skill import Rowsblock, HenriqueSkill
from henrique.main.tool.skillnote_tool import SkillnoteTool
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]

class TradegoodSkill:
    CODENAME = "tradegood"

    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity}

    @classmethod
    def _entity_lang2response(cls, entity, lang):
        entity_type = Entity.entity2type(entity)
        codename = Entity.entity2value(entity)

        from henrique.main.skill.tradegood.tradegood_port.tradegood_port_response import TradegoodPortResponse
        from henrique.main.skill.tradegood.tradegood_tradegood.tradegood_tradegood_response import TradegoodTradegoodResponse
        from henrique.main.skill.tradegood.tradegood_culture.tradegood_culture_response import TradegoodCultureResponse

        h_type2func = {PortEntity.TYPE: partial(TradegoodPortResponse.codename_lang2text, lang=lang),
                       TradegoodEntity.TYPE: partial(TradegoodTradegoodResponse.codename_lang2text, lang=lang),
                       CultureEntity.TYPE: partial(TradegoodCultureResponse.codename_lang2text, lang=lang),
                       }

        assert_equals(set(h_type2func.keys()), smap(lambda c: c.TYPE, cls.target_entity_classes()))

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
        config = {Entity.Config.Field.LOCALE: locale}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=Entity.entity2span)

        response = Rowsblock.blocks2text([cls._entity_lang2response(entity, lang) for entity in entity_list])
        return response




