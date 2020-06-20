import logging
import os
import sys

import pytz
import yaml

from foxylib.tools.function.warmer import Warmer

from foxylib.tools.datetime.date_tools import DatetimeTool, TimedeltaTool
from functools import lru_cache

from datetime import timedelta, datetime
from random import choice

from foxylib.tools.arithmetic.arithmetic_tool import ArithmeticTool
from foxylib.tools.collections.collections_tool import lchain, zip_strict, l_singleton2obj
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.yaml_tool import YAMLTool

from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from henrique.main.document.chatroomuser.entity.chatroomuser_entity import ChatroomuserEntity
from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.henrique_entity import HenriqueEntity
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

        v = FoxylibEntity.entity2value(entity)
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
    def server_lang2lookup(cls, server_codename, lang):
        from henrique.main.skill.nanban.timedelta.nanban_timedelta import NanbanTimedelta

        server = Server.codename2server(server_codename)
        str_timedelta = NanbanTimedelta.server_lang2str(server_codename, lang)
        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
        data = {"server": Server.server_lang2name(server, lang),
                "str_timedelta": str_timedelta,
                }
        str_out = HenriqueJinja2.textfile2text(filepath, data)
        return str_out

    @classmethod
    def server_datetime_lang2update(cls, server_codename, dt_this, lang):
        # server = Server.codename2server(server_codename)
        doc_this = {ServerDoc.Field.CODENAME: server_codename,
                    ServerDoc.Field.NANBAN_TIME: dt_this,
                    }
        ServerDoc.docs2upsert([doc_this])
        # doc_post = ServerDoc.codename2doc(server_codename)
        # return doc_post

    @classmethod
    def server_relativedelta_lang2update(cls, server_codename, reldelta, lang):
        # server = Server.codename2server(server_codename)
        doc_prev = ServerDoc.codename2doc(server_codename)
        nanban_time_prev = ServerDoc.doc2nanban_time(doc_prev)
        nanban_time_this = nanban_time_prev + reldelta

        doc_this = {ServerDoc.Field.CODENAME: server_codename,
                    ServerDoc.Field.NANBAN_TIME: nanban_time_this,
                    }
        ServerDoc.docs2upsert([doc_this])
        # doc_post = ServerDoc.codename2doc(server_codename)
        # return doc_post

    @classmethod
    def entity_classes(cls):
        return {RelativeTimedeltaEntity, DatetimeEntity, }

    @classmethod
    def packet2response(cls, packet):
        logger = HenriqueLogger.func_level2logger(cls.packet2response, logging.DEBUG)
        logger.debug({"packet":packet})

        server_codename = HenriquePacket.packet2server(packet)
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale)

        text_in = KhalaPacket.packet2text(packet)
        config = {HenriqueEntity.Config.Field.LOCALE: locale}
        # entity_list = RelativeTimedeltaEntity.text2entity_list(text_in, config=config)

        entity_list = HenriqueEntity.text_extractors2entity_list(text_in, cls.entity_classes(), config=config)

        if not entity_list:
            return cls.server_lang2lookup(server_codename, lang)

        if len(entity_list) != 1:
            return  # Invalid request

        entity = l_singleton2obj(entity_list)

        if FoxylibEntity.entity2type(entity) == RelativeTimedeltaEntity.entity_type():
            reldelta = RelativeTimedeltaEntity.entity2relativedelta(entity)
            cls.server_relativedelta_lang2update(server_codename, reldelta, lang)

        if FoxylibEntity.entity2type(entity) == DatetimeEntity.entity_type():
            dt = DatetimeEntity.entity2datetime(entity)
            cls.server_datetime_lang2update(server_codename, dt, lang)



