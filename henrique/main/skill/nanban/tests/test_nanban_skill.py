import logging
from unittest import TestCase

from henrique.main.document.server.server import Server
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.nanban.nanban_skill import NanbanSkill
from khala.document.chatroom.chatroom import Chatroom
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestNanbanSkill(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    # def test_01(self):
    #     Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
    #
    #     hyp = NanbanSkill.server_datetime_lang2update(Server.Codename.MARIS, "ko")
    #
    # def test_02(self):
    #     Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
    #
    #     hyp = NanbanSkill.server_relativedelta_lang2update(Server.Codename.MARIS, "ko")
    #
    # def test_03(self):
    #     Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])
    #
    #     hyp = NanbanSkill.server_lang2lookup(Server.Codename.MARIS, "ko")
    #     # sender_name = "iris"
    #     # channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
    #     # ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])
    #     #
    #     # packet = {KhalaPacket.Field.TEXT: "?누구 나",
    #     #           KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
    #     #           KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
    #     #           KhalaPacket.Field.SENDER_NAME: sender_name,
    #     #           }
    #     #
    #     # response = WhoSkill.packet2response(packet)
    #
    #     # pprint(response)
    #
    #     self.assertGreaterEqual(len(response.splitlines()), 3)
    #     self.assertEqual(response.splitlines()[0], "[유저] iris")



