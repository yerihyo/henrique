from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestPortSkill(TestCase):
    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT: "?port 리스본",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = PortSkill.packet2response(packet)
        ref = """[항구] 리스본
- 문화권: 이베리아
- 내성: 식료품, 가축, 조미료, 주류, 기호품, 광석, 무기류, 공예품, 총포류"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        packet = {KhalaPacket.Field.TEXT: "?port 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = PortSkill.packet2response(packet)
        # ref = ("[이베리아] 항구 - 세비야, 세우타, 카사블랑카, 라스팔마스, 마데이라, 파루, 리스본, 포르투, 비아나두카스텔루, 히혼, "
        #        "빌바오, 말라가, 발렌시아, 팔마, 바르셀로나, 몽펠리에, 사그레스")
        ref = """[항구] 이베리아 문화권
- 라스팔마스, 파루, 카사블랑카, 히혼, 팔마, 마데이라, 비아나두카스텔루, 리스본, 사그레스, 빌바오, 세비야, 바르셀로나, 포르투, 말라가, 세우타, 몽펠리에, 발렌시아"""

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)


