from pprint import pprint
from unittest import TestCase

from henrique.main.skill.port.port_skill import PortSkill
from henrique.main.skill.port.port_skill_description import PortSkillDescription
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestHelpSkillDescription(TestCase):
    def test_01(self):

        description = PortSkillDescription.lang2text("ko")

        # pprint({"description":description})
        self.assertTrue(description.startswith("?도움말 명령어"))

