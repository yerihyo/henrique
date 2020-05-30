import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.who.who_skill import WhoSkill
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestWhoSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        packet = {KhalaPacket.Field.TEXT: "?누구 나",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        response = WhoSkill.packet2response(packet)

        # pprint(response)

        self.assertGreaterEqual(len(response.splitlines()), 3)
        self.assertEqual(response.splitlines()[0], "[iris]")

    def test_02(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        packet = {KhalaPacket.Field.TEXT: "?누구 iris",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        response = WhoSkill.packet2response(packet)

        # pprint(response)

        self.assertGreaterEqual(len(response.splitlines()), 3)
        self.assertEqual(response.splitlines()[0], "[iris(아리)]")


