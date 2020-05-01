import logging
from pprint import pprint
from unittest import TestCase

import pytest

from henrique.main.handlers.khala.packet_handler import PacketHandler
from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_skill import PortSkill
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket, KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestHenriqueKhala(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT: "?항구 리스본",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: ChannelUserKakaotalk.sender_name2codename("iris"),
                  KhalaPacket.Field.SENDER_NAME: "iris",
                  }
        hyp = HenriqueKhala.packet2response(packet)
        ref = "[리스본]"

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        chatroom = {'channel': 'discord', 'codename': 'discord-471024213159837696', 'locale': 'ko-KR'}
        Chatroom.chatrooms2upsert([chatroom])

        channel_user = {'channel': 'discord', 'codename': 'discord-340205035558535169', 'alias': 'yeri'}
        ChannelUser.channel_users2upsert([channel_user])

        packet = {'text': '?ㅎㄱ 육두구',
                  'chatroom': 'discord-471024213159837696',
                  'channel_user': 'discord-340205035558535169',
                  'sender_name': 'yeri',
        }
        hyp = HenriqueKhala.packet2response(packet)
        ref = "[육두구] 취급항 - 룬, 암보이나"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
