from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from henrique.main.skill.tradegood.tradegood_skill import TradegoodSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestTradegoodSkill(TestCase):
    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT:"?tradegood 육두구",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = TradegoodSkill.packet2response(packet)
        ref = '[교역품] 육두구'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT:"?tradegood 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = TradegoodSkill.packet2response(packet)
        ref = """[교역품] 이베리아 문화권 우대품
- 타네가시마 총
- 대만 목각
- 유자
- 일본서적
- 사마 은
- 스타아니스
- 호필
- 두반장
- 가는 끈
- 산초
- 진달래
- 진과스 금
- 청룡도
- 사슴 가죽
- 한지
- 자근
- 사다장"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
