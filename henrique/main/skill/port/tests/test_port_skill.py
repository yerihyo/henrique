from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestPortSkill(TestCase):
    def test_01(self):

        packet = {KhalaPacket.Field.TEXT:"?port 리스본",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = PortSkill.packet2response(packet)
        ref = '[리스본]'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)

    def test_02(self):

        packet = {KhalaPacket.Field.TEXT:"?port 이베리아",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  }

        hyp = PortSkill.packet2response(packet)
        ref = '[이베리아] 항구 - 라스팔마스, 파루, 카사블랑카, 히혼, 팔마, 마데이라, 비아나두카스텔루, 리스본, 사그레스, 빌바오, 세비야, 바르셀로나, 포르투, 말라가, 세우타, 몽펠리에, 발렌시아'

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)
