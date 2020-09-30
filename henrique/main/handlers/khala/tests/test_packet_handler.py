import logging
from pprint import pprint
from unittest import TestCase

import pytest

from henrique.main.handlers.khala.packet_handler import PacketHandler
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_skill import PortSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket, KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk


class TestHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        logger = HenriqueLogger.func_level2logger(self.test_01, logging.DEBUG)

        packet = {
            KhalaPacket.Field.TEXT: "?항구 리스본",
            KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
            KhalaPacket.Field.CHANNEL_USER: ChannelUserKakaotalk.sender_name2codename("iris"),
            KhalaPacket.Field.SENDER_NAME: "iris",
        }

        # pprint(packet)

        hyp = PacketHandler.post(packet)
        ref = ("""[항구] 리스본
- 문화권: 이베리아
- 내성: 식료품, 가축, 조미료, 주류, 기호품, 광석, 무기류, 공예품, 총포류""", 200)

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        packet = {'channel_user': 'kakaotalk_uwo.iris',
                  'chatroom': 'kakaotalk_uwo.uwo',
                  'sender_name': 'iris',
                  'text': '?항구 리스본'
                  }

        hyp = PacketHandler.post(packet)
        ref = ("""[항구] 리스본
- 문화권: 이베리아
- 내성: 식료품, 가축, 조미료, 주류, 기호품, 광석, 무기류, 공예품, 총포류""", 200)

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_03(self):
        packet = {'channel_user': 'kakaotalk_uwo.iris',
                  'chatroom': 'kakaotalk_uwo.uwo',
                  'sender_name': 'iris',
                  'text': '?ㄱㅇㅍ 리스본',
        }

        hyp = PacketHandler.post(packet)
        ref = ("""[교역품] 리스본 교역소
- 햄
- 아몬드유
- 닭
- 서양 서적
- 브랜디
- 동광석
- 아몬드
- 도자기
- 단검
- 포탄""",
 200)

        # pprint(hyp)
        self.assertEqual(hyp, ref)
