from pprint import pprint
from unittest import TestCase

from henrique.main.skill.culture.culture_skill import CultureSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestCultureSkill(TestCase):
    def test_01(self):

        packet = {KhalaPacket.Field.TEXT:"?ㅁㅎ 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = '[이베리아]'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT:"?culture Lisbon",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = '[리스본] 문화권 - 이베리아'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_03(self):
        packet = {KhalaPacket.Field.TEXT: "?culture 복분자",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = CultureSkill.packet2response(packet)
        ref = """[복분자] 우대 문화권
- 북유럽"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
