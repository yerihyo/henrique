from pprint import pprint
from unittest import TestCase

from henrique.main.skill.culture.culture_skill import CultureSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestCultureSkill(TestCase):
    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT:"?ㅁㅎ 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = '[이베리아]'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT:"?culture Lisbon",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = '[문화권] 리스본: 이베리아 문화권'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_03(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT: "?culture 복분자",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = """[문화권] 복분자 우대 문화권
- 북유럽"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
