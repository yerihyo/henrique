import logging
import os
import sys

from foxylib.tools.function.warmer import Warmer
from functools import partial, lru_cache

from datetime import datetime, timedelta
from random import choice

import pytz
from future.utils import lmap

from foxylib.tools.collections.collections_tool import l_singleton2obj
from foxylib.tools.datetime.datetime_tool import DatetimeTool, TimeTool, Nearest
from foxylib.tools.datetime.pytz_tool import PytzTool
from foxylib.tools.datetime.timezone.timezone_tool import TimezoneTool
from foxylib.tools.entity.calendar.time.time_entity import TimeEntity
from foxylib.tools.entity.entity_tool import FoxylibEntity
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.string.string_tool import str2strip
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from henrique.main.document.chatroomuser.entity.chatroomuser_entity import ChatroomuserEntity
from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.document.server.mongodb.server_doc import ServerDoc, ServerNanban
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.error.command_error import HenriqueCommandError
from henrique.main.singleton.jinja2.henrique_jinja2 import HenriqueJinja2
from henrique.main.singleton.khala.henrique_khala import HenriquePacket
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.nanban.timedelta.nanban_timedelta import NanbanTimedeltaSuffix, NanbanTimedelta
from henrique.main.tool.entity.datetime.timedelta.timedelta_entity import RelativeTimedeltaEntity
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class NanbanSkillError:
    class Codename:
        NO_PREV_NANBAN_ERROR = "NO_PREV_NANBAN_ERROR"

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def yaml(cls):
        filepath = os.path.join(FILE_DIR, "error.yaml")
        j = YAMLTool.filepath2j(filepath)
        return j

    @classmethod
    def codename_lang2text(cls, codename, lang):
        return JsonTool.down(cls.yaml(), [codename, lang])


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
        logger = HenriqueLogger.func_level2logger(cls.server_lang2lookup, logging.DEBUG)

        server = Server.codename2server(server_codename)
        utc_now = datetime.now(pytz.utc)
        datetime_nanban = NanbanTimedelta.server2datetime_nanban(server_codename, utc_now)
        logger.debug({"datetime_nanban":datetime_nanban})

        def datetime_nanban2str_out(dt_nanban):
            filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))
            has_dt_nanban = (dt_nanban is not None)
            if not has_dt_nanban:
                data = {"server": Server.server_lang2name(server, lang),
                        "has_dt_nanban": has_dt_nanban,
                        }
                str_out = HenriqueJinja2.textfile2text(filepath, data)
                return str_out

            td_nanban = dt_nanban - utc_now

            tzdb = HenriqueLocale.lang2tzdb(lang)

            str_timedelta_nanban = NanbanTimedelta.timedelta_lang2text(td_nanban, lang)

            logger.debug({"server_codename": server_codename,
                          "server": server,
                          "dt_nanban": dt_nanban,
                          })

            data = {"server": Server.server_lang2name(server, lang),
                    "dt_nanban": NanbanTimedelta.datetime2text(dt_nanban, tzdb),
                    "dt_now": NanbanTimedelta.datetime2text(utc_now, tzdb),
                    "timedelta_nanban": str_timedelta_nanban,
                    "has_dt_nanban": has_dt_nanban,
                    }
            str_out = HenriqueJinja2.textfile2text(filepath, data)
            return str_out

        return datetime_nanban2str_out(datetime_nanban)

    @classmethod
    def relativedelta2nanban_datetime(cls, server_codename, reldelta):
        doc_prev = ServerDoc.codename2doc(server_codename)
        if not doc_prev:
            return None

        nanban_prev = ServerDoc.doc2nanban(doc_prev)
        if not nanban_prev:
            return None

        nanban_datetime_prev = ServerNanban.nanban2datetime(nanban_prev)
        nanban_datetime_new = nanban_datetime_prev + reldelta
        return nanban_datetime_new

    @classmethod
    def nanban_datetime2upsert_mongo(cls, packet, datetime_nanban,):
        logger = HenriqueLogger.func_level2logger(cls.nanban_datetime2upsert_mongo, logging.DEBUG)

        server_codename = HenriquePacket.packet2server(packet)
        text_in = KhalaPacket.packet2text(packet)

        # server = Server.codename2server(server_codename)
        dt_utc = DatetimeTool.astimezone(datetime_nanban, pytz.utc)
        # raise Exception({"datetime_in":datetime_in,"dt_utc":dt_utc})

        nanban = {ServerNanban.Field.DATETIME: dt_utc,
                  ServerNanban.Field.COMMAND_IN: text_in,
                  }
        doc_this = {ServerDoc.Field.CODENAME: server_codename,
                    ServerDoc.Field.NANBAN: nanban,
                    }
        logger.debug({"datetime_nanban":datetime_nanban,
                      "doc_this":doc_this,
                      })
        ServerDoc.docs2upsert([doc_this])
        # doc_post = ServerDoc.codename2doc(server_codename)
        # return doc_post

    # @classmethod
    # def server_relativedelta_lang2update(cls, server_codename, reldelta, lang):
    #     # server = Server.codename2server(server_codename)
    #     doc_prev = ServerDoc.codename2doc(server_codename)
    #     dt_nanban_prev = ServerDoc.doc2datetime_nanban(doc_prev)
    #     dt_nanban_this = dt_nanban_prev + reldelta
    #
    #     doc_this = {ServerDoc.Field.CODENAME: server_codename,
    #                 ServerDoc.Field.DATETIME_NANBAN: dt_nanban_this,
    #                 }
    #     ServerDoc.docs2upsert([doc_this])
        # doc_post = ServerDoc.codename2doc(server_codename)
        # return doc_post

    @classmethod
    def config2extractors(cls, config):
        return {partial(RelativeTimedeltaEntity.text2entity_list, config=config),
                TimeEntity.text2entity_list,
                }

    @classmethod
    def packet2response(cls, packet):
        logger = HenriqueLogger.func_level2logger(cls.packet2response, logging.DEBUG)
        logger.debug({"packet":packet})


        server_codename = HenriquePacket.packet2server(packet)
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        locale = Chatroom.chatroom2locale(chatroom) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale)
        tz = pytz.timezone(HenriqueLocale.lang2tzdb(lang))
        dt_now = datetime.now(tz)

        text_in = KhalaPacket.packet2text(packet)
        config = {HenriqueEntity.Config.Field.LOCALE: locale}
        # entity_list = RelativeTimedeltaEntity.text2entity_list(text_in, config=config)

        entity_list = HenriqueEntity.text_extractors2entity_list(text_in, cls.config2extractors(config),)
        logger.debug({"len(entity_list)": len(entity_list),
                      "entity_list": entity_list,
                      })

        if not entity_list:
            return cls.server_lang2lookup(server_codename, lang)

        if len(entity_list) != 1:
            return  # Invalid request

        entity = l_singleton2obj(entity_list)
        if FoxylibEntity.entity2type(entity) == RelativeTimedeltaEntity.entity_type():
            reldelta = RelativeTimedeltaEntity.entity2relativedelta(entity)
            dt_in = cls.relativedelta2nanban_datetime(server_codename, reldelta, )

            if dt_in is None:
                msg_error = NanbanSkillError.codename_lang2text(NanbanSkillError.Codename.NO_PREV_NANBAN_ERROR, lang)
                raise HenriqueCommandError(msg_error)

            logger.debug({"reldelta": reldelta,})

        elif FoxylibEntity.entity2type(entity) == TimeEntity.entity_type():
            time_in = TimeEntity.value2datetime_time(FoxylibEntity.entity2value(entity))
            dt_in = PytzTool.localize(datetime.combine(dt_now.date(), time_in), tz)
            logger.debug({"time_in": time_in, })
        else:
            raise RuntimeError({"Invalid entity type: {}".format(FoxylibEntity.entity2type(entity))})

        dt_nearest = DatetimeTool.datetime2nearest(dt_in, dt_now, NanbanTimedelta.period(), Nearest.COMING)

        logger.debug({"text_in": text_in,
                      "dt_now": dt_now,
                      "dt_in":dt_in,
                      "dt_nearest": dt_nearest,
                      })

        cls.nanban_datetime2upsert_mongo(packet, dt_nearest)
        return cls.server_lang2lookup(server_codename, lang)
