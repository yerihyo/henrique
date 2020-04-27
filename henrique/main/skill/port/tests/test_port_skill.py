from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestPortSkill(TestCase):
    def test_01(self):
        packet = {KhalaPacket.Field.TEXT: "?port 리스본",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = PortSkill.packet2response(packet)
        ref = '[리스본]'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT: "?port 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  }

        hyp = PortSkill.packet2response(packet)
        ref = ("[이베리아] 항구 - 세비야, 세우타, 카사블랑카, 라스팔마스, 마데이라, 파루, 리스본, 포르투, 비아나두카스텔루, 히혼, "
               "빌바오, 말라가, 발렌시아, 팔마, 바르셀로나, 몽펠리에, 사그레스")

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
