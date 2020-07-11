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


class TestNoticeSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
        ServerDoc.codenames2delete([Server.Codename.MARIS])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        # now_utc = datetime.now(pytz.utc)
        packet = {KhalaPacket.Field.TEXT: "?공지",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        hyp = HenriquePacket.packet2response(packet)
        ref = "[공지] 다음과 같은 공지사항이 있어요:"

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
        ServerDoc.codenames2delete([Server.Codename.MARIS])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        # now_utc = datetime.now(pytz.utc)
        packet = {KhalaPacket.Field.TEXT: "?공지 소개",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        hyp = HenriquePacket.packet2response(packet)
        ref = "[공지] 소개"

        # pprint(hyp)
        self.assertEqual(hyp, ref)

