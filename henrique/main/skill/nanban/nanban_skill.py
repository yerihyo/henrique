import logging
import os
import sys

import pytz
import yaml

from foxylib.tools.function.warmer import Warmer

from foxylib.tools.date.date_tools import DatetimeTool, TimedeltaTool
from functools import lru_cache

from datetime import timedelta, datetime
from random import choice

from foxylib.tools.arithmetic.arithmetic_tool import ArithmeticTool
from foxylib.tools.collections.collections_tool import lchain, zip_strict
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.yaml_tool import YAMLTool

from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from henrique.main.document.chatroomuser.entity.chatroomuser_entity import ChatroomuserEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.server.mongodb.server_doc import ServerDoc
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import Rowsblock, HenriquePacket
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.tool.entity.time.timedelta.timedelta_entity import RelativeTimedeltaEntity, TimedeltaUnit
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class NanbanSkill:
    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.nanban.nanban_skill_description import NanbanSkillDescription
        return NanbanSkillDescription.lang2text(lang)

    # @classmethod
    # def target_entity_classes(cls):
    #     return {RelativeTimedeltaEntity,}

    @classmethod
    def entity2response_block(cls, entity, packet, ):
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
    def response_lookup(cls, server, lang):
        from henrique.main.skill.nanban.timedelta.nanban_timedelta import NanbanTimedelta



        filepath = os.path.join(FILE_DIR, "tmplt.ko.part.txt")
        data = {"server": Server.server_lang2name(server, lang),
                "nanban_time": NanbanTimedelta.server_lang2str(server, lang),
                }
        str_out = HenriqueJinja2.textfile2text(filepath, data)
        return str_out

    @classmethod
    def response_update(cls, reldelta, lang):
        pass



    @classmethod
    def packet2response(cls, packet):
        logger = HenriqueLogger.func_level2logger(cls.packet2response, logging.DEBUG)
        logger.debug({"packet":packet})

        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale)

        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE: locale}
        entity_list = RelativeTimedeltaEntity.text2entity_list(text_in, config=config)

        server = Server.codename2server(HenriquePacket.packet2server(packet))

        if not entity_list:
            return cls.response_lookup(server, lang)

        if len(entity_list) == 1:
            entity = entity_list
            reldelta = RelativeTimedeltaEntity.entity2relativedelta(entity)
            return cls.response_update(server, reldelta, lang)

