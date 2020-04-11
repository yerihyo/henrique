import os
import sys

from functools import partial
from future.utils import lmap
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.skill.henrique_skill import Rowsblock
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortSkill:
    CODENAME = "port"

    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity}

    @classmethod
    def _entity_lang2response_block(cls, entity, lang):
        entity_type = Entity.entity2type(entity)
        codename = Entity.entity2value(entity)

        from henrique.main.skill.port.port_port.port_port_response import PortPortResponse
        from henrique.main.skill.port.port_tradegood.port_tradegood_response import PortTradegoodResponse
        from henrique.main.skill.port.port_culture.port_culture_response import PortCultureResponse

        h_type2func = {PortEntity.TYPE: partial(PortPortResponse.codename_lang2text, lang=lang),
                       TradegoodEntity.TYPE: partial(PortTradegoodResponse.codename_lang2text, lang=lang),
                       CultureEntity.TYPE: partial(PortCultureResponse.codename_lang2text, lang=lang),
                       }

        assert_equals(set(h_type2func.keys()), smap(lambda c: c.TYPE, cls.target_entity_classes()))

        codename2response = h_type2func.get(entity_type)
        if not codename2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        return codename2response(codename)


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

        blocks = [cls._entity_lang2response_block(entity, lang) for entity in entity_list]

        return Rowsblock.blocks2text(blocks)

