from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from henrique.main.skill.port.port_skill_description import PortSkillDescription
from henrique.main.skill.price.price_skill_description import PriceSkillDescription
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestPriceSkillDescription(TestCase):
    def test_01(self):

        description = PriceSkillDescription.lang2text("ko")

        # pprint({"description":description})
        self.assertTrue(description.startswith("?시세 명령어"))

