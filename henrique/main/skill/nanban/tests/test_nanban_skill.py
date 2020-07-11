import logging
import os
from pprint import pprint

import pytz
from datetime import datetime, timedelta, time
from unittest import TestCase

from foxylib.tools.collections.collections_tool import ListTool
from foxylib.tools.datetime.datetime_tool import DatetimeTool
from foxylib.tools.datetime.pytz_tool import PytzTool
from foxylib.tools.span.span_tool import SpanTool
from henrique.main.document.server.mongodb.server_doc import ServerCollection, ServerDoc, ServerNanban
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.error.command_error import HenriqueCommandError
from henrique.main.singleton.khala.henrique_khala import HenriquePacket
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.nanban.nanban_skill import NanbanSkill
from henrique.main.skill.nanban.timedelta.nanban_timedelta import NanbanTimedelta
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import Chatroom, KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestNanbanSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    @classmethod
    def response2hyp(cls, response):
        l = response.splitlines()
        return "\n".join([l[0], l[2]])

    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        now_utc = datetime.now(pytz.utc)
        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        packet = {KhalaPacket.Field.TEXT: "?남만 지금",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        NanbanSkill.nanban_datetime2upsert_mongo(packet, now_utc,)

        response = NanbanSkill.server_lang2lookup(Server.Codename.MARIS, "ko")
        hyp = "\n".join(ListTool.indexes2filtered(response.splitlines(), [0, 2]))

        utc_nanban = now_utc + NanbanTimedelta.period()
        tz = pytz.timezone("Asia/Seoul")

        # now_tz = DatetimeTool.astimezone(now_utc, tz)
        now_nanban = DatetimeTool.astimezone(utc_nanban, tz)

        ref = """[남만시각] 글로벌서버
다음 남만 시각: {} (KST) / 약 2시간 후""".format(now_nanban.strftime("%I:%M:%S %p").lstrip("0"))

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        logger = HenriqueLogger.func_level2logger(self.test_02, logging.DEBUG)

        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        now_seoul = datetime.now(tz=pytz.timezone(HenriqueLocale.lang2tzdb("ko")))
        dt_nanban = now_seoul + timedelta(seconds=3 * 60)
        text = "?남만 {}".format(dt_nanban.strftime("%I:%M %p").lstrip("0"))
        logger.debug({"text": text, "now_seoul": now_seoul, })

        packet = {KhalaPacket.Field.TEXT: text,
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        response = NanbanSkill.packet2response(packet)

        # pprint(text)
        # pprint(response)

        response_lines = response.splitlines()

        span = (len("다음 남만 시각: "),
                len("다음 남만 시각: 3:58:00 PM (KST) "),
                )

        hyp = SpanTool.list_span2sublist(response_lines[2], span).strip()
        ref = dt_nanban.strftime("%I:%M:00 %p (KST)").lstrip("0")
        self.assertEqual(hyp, ref, )

        # hyp = response.splitlines()[0]

        # utc_nanban = now_utc + NanbanTimedelta.period()
        # tz = pytz.timezone("Asia/Seoul")

        # now_tz = DatetimeTool.astimezone(now_utc, tz)
        # now_nanban = DatetimeTool.astimezone(utc_nanban, tz)

        # ref = """[남만시각] 글로벌서버"""
        #
        # pprint(response)
        # self.assertEqual(hyp, ref)

    def test_03(self):
        logger = HenriqueLogger.func_level2logger(self.test_02, logging.DEBUG)

        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        now_seoul = datetime.now(tz=pytz.timezone(HenriqueLocale.lang2tzdb("ko")))
        dt_target = now_seoul - timedelta(seconds=3 * 60)
        text = "?남만 {}".format(dt_target.strftime("%I:%M %p").lstrip("0"))
        logger.debug({"text": text, "now_seoul": now_seoul, })

        packet = {KhalaPacket.Field.TEXT: text,
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        response = NanbanSkill.packet2response(packet)

        # pprint(text)
        # pprint(response)

        response_lines = response.splitlines()

        span = (len("다음 남만 시각: "),
                len("다음 남만 시각: 3:58:00 PM (KST) "),
                )

        hyp = SpanTool.list_span2sublist(response_lines[2], span).strip()
        dt_nanban = dt_target + NanbanTimedelta.period()
        ref = dt_nanban.strftime("%I:%M:00 %p (KST)").lstrip("0")
        self.assertEqual(hyp, ref, )

        # hyp = response.splitlines()[0]

        # utc_nanban = now_utc + NanbanTimedelta.period()
        # tz = pytz.timezone("Asia/Seoul")

        # now_tz = DatetimeTool.astimezone(now_utc, tz)
        # now_nanban = DatetimeTool.astimezone(utc_nanban, tz)

        # ref = """[남만시각] 글로벌서버"""
        #
        # pprint(response)
        # self.assertEqual(hyp, ref)

    def test_04(self):
        cls = self.__class__

        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        # now_utc = datetime.now(pytz.utc)
        packet = {KhalaPacket.Field.TEXT: "?남만",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        response = NanbanSkill.packet2response(packet)
        hyp = response.splitlines()[0]

        # utc_nanban = now_utc + NanbanTimedelta.period()
        # tz = pytz.timezone("Asia/Seoul")

        # now_tz = DatetimeTool.astimezone(now_utc, tz)
        # now_nanban = DatetimeTool.astimezone(utc_nanban, tz)

        ref = """[남만시각] 글로벌서버"""

        # pprint(response)
        self.assertEqual(hyp, ref)

    def test_05(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
        ServerDoc.codenames2delete([Server.Codename.MARIS])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        # now_utc = datetime.now(pytz.utc)
        packet = {KhalaPacket.Field.TEXT: "?남만 +2분",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        with self.assertRaises(HenriqueCommandError) as context:
            NanbanSkill.packet2response(packet)

        self.assertEquals("""[남만시각] 이전에 설정된 남만 시각이 없어서 +/-로 남만 시각을 조정할 수 없어요.""", str(context.exception))

        if HenriqueEnv.env() == HenriqueEnv.Value.LOCAL:
            return  # cannot test here because LOCAL has different settings

        hyp = HenriquePacket.packet2response(packet)
        ref = "[남만시각] 이전에 설정된 남만 시각이 없어서 +/-로 남만 시각을 조정할 수 없어요."

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_06(self):
        logger = HenriqueLogger.func_level2logger(self.test_06, logging.DEBUG)

        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
        ServerDoc.codenames2delete([Server.Codename.MARIS])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        tz = pytz.timezone("Asia/Seoul")
        now_tz = DatetimeTool.datetime2truncate_seconds(datetime.now(tz))
        # hour = (now_tz + timedelta(seconds=3600)).hour

        packet1 = {KhalaPacket.Field.TEXT: "?남만 {}".format(now_tz.strftime("%I:%M %p")),
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        NanbanSkill.packet2response(packet1)

        packet2 = {KhalaPacket.Field.TEXT: "?남만 +2분 1초",
                   KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                   KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                   KhalaPacket.Field.SENDER_NAME: sender_name,
                   }

        NanbanSkill.packet2response(packet2)

        doc = ServerDoc.codename2doc(Server.Codename.MARIS)

        dt_nanban = DatetimeTool.astimezone(ServerNanban.nanban2datetime(ServerDoc.doc2nanban(doc)), tz)

        logger.debug({"now_tz":now_tz,
                      "dt_nanban":dt_nanban,
                      'now_tz.strftime("%I:%M %p")':now_tz.strftime("%I:%M %p"),
                      })
        ref = (now_tz + timedelta(seconds=2 * 60 + 1)).timetz()
        self.assertEquals(dt_nanban.timetz(), ref)
