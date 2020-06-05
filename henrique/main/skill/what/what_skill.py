import os

from functools import partial
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.document.chatroomuser.entity.chatroomuser_entity import ChatroomuserEntity
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.skill.culture.culture_skill import CultureSkill
from henrique.main.skill.port.port_skill import PortSkill
from henrique.main.skill.tradegood.tradegood_skill import TradegoodSkill
from henrique.main.skill.who.who_skill import WhoSkill
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class WhatSkill:
    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.what.what_skill_description import WhatSkillDescription
        return WhatSkillDescription.lang2text(lang)

    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity, ChatroomuserEntity,
                # TradegoodtypeEntity, ServerEntity,
                }

    @classmethod
    def entity2response_block(cls, packet, entity,):
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom)
        lang = LocaleTool.locale2lang(locale)

        entity_type = Entity.entity2type(entity)

        h_type2func = {PortEntity.entity_type(): partial(PortSkill.entity_lang2response_block, lang=lang),
                       TradegoodEntity.entity_type(): partial(TradegoodSkill.entity_lang2response_block, lang=lang),
                       CultureEntity.entity_type(): partial(CultureSkill.entity_lang2response_block, lang=lang),
                       ChatroomuserEntity.entity_type(): partial(WhoSkill.entity2response_block, packet=packet,),
                       }

        assert_equals(set(h_type2func.keys()), smap(lambda c: c.entity_type(), cls.target_entity_classes()))

        entity2response = h_type2func.get(entity_type)
        if not entity2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        return entity2response(entity)

    @classmethod
    def packet2response(cls, packet):
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom)

        entity_classes = cls.target_entity_classes()
        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE: locale}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=Entity.entity2span)

        blocks = [cls.entity2response_block(packet, entity) for entity in entity_list]

        return Rowsblock.blocks2text(blocks)



