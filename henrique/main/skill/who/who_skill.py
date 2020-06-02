import logging
import os
from random import choice

from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from henrique.main.document.chatroomuser.entity.chatroomuser_entity import ChatroomuserEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import Rowsblock
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class WhoSkill:
    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.who.who_skill_description import WhoSkillDescription
        return WhoSkillDescription.lang2text(lang)

    @classmethod
    def target_entity_classes(cls):
        return {ChatroomuserEntity,}

    @classmethod
    def entity2response_block(cls, packet, entity, ):
        logger = HenriqueLogger.func_level2logger(cls.packet2response, logging.DEBUG)

        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        if Chatroom.chatroom2codename(chatroom) != ChatroomKakaotalk.codename():
            return

        locale = Chatroom.chatroom2locale(chatroom)
        lang = LocaleTool.locale2lang(locale)

        v = Entity.entity2value(entity)
        codename = ChatroomuserEntity.value_packet2codename(v, packet)
        logger.debug({"codename": codename,
                      "entity": entity,
                      "v": v,
                      })

        chatroomuser = Chatroomuser.codename2chatroomuser(codename)

        comments = Chatroomuser.chatroomuser2comments(chatroomuser)
        comment = choice(comments) if comments else None

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"name": codename,
                "comment": comment,
                "str_aliases": ", ".join(Chatroomuser.chatroomuser2aliases(chatroomuser)),
                }
        text_out = str2strip(HenriqueJinja2.textfile2text(filepath, data))

        return text_out

    @classmethod
    def packet2response(cls, packet):
        logger = HenriqueLogger.func_level2logger(cls.packet2response, logging.DEBUG)

        logger.debug({"packet":packet})

        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        if Chatroom.chatroom2codename(chatroom) != ChatroomKakaotalk.codename():
            return

        text_in = KhalaPacket.packet2text(packet)
        # config = {Entity.Config.Field.LOCALE: locale}

        # config = {Entity.Config.Field.LOCALE: locale}
        # entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])
        #
        entity_list_chatroomuser = sorted(ChatroomuserEntity.text2entity_list(text_in), key=Entity.entity2span)
        blocks = [cls.entity2response_block(packet, entity) for entity in entity_list_chatroomuser]

        return Rowsblock.blocks2text(blocks)



