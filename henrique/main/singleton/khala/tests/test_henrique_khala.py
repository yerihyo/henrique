import logging
from unittest import TestCase

from henrique.main.singleton.khala.henrique_khala import HenriquePacket
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestHenriquePacket(TestCase):
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
        hyp = HenriquePacket.packet2response(packet)
        ref = """[항구] 리스본
- 문화권: 이베리아
- 내성: 식료품, 가축, 조미료, 주류, 기호품, 광석, 무기류, 공예품, 총포류"""

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
        hyp = HenriquePacket.packet2response(packet)
        ref = """[항구] 육두구 취급항 - 룬, 암보이나"""

        # pprint(hyp)
        self.assertEqual(hyp, ref)
