from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from henrique.main.skill.port.port_skill_description import PortSkillDescription
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestPortSkillDescription(TestCase):
    def test_01(self):

        description = PortSkillDescription.lang2text("ko")

        pprint(description)
        self.assertTrue(description.startswith("?항구 명령어"))

