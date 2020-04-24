import logging
from pprint import pprint
from unittest import TestCase

import pytest

from henrique.main.handlers.khala.packet_handler import PacketHandler
from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_skill import PortSkill
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket, KhalaPacket


class TestHenriqueKhala(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?항구 리스본",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  KhalaPacket.Field.CHANNEL_USER: KakaotalkUWOChannel.username2channel_user_codename("iris"),
                  KhalaPacket.Field.SENDER_NAME: "iris",
                  }
        hyp = HenriqueKhala.packet2response(packet)
        ref = "[리스본]"

        # pprint(hyp)
        self.assertEqual(hyp, ref)
