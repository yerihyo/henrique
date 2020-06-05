from pprint import pprint
from unittest import TestCase

from henrique.main.skill.who.who_skill_description import WhoSkillDescription


class TestWhoSkillDescription(TestCase):
    def test_01(self):

        description = WhoSkillDescription.lang2text("ko")

        pprint(description)
        self.assertTrue(description.startswith("?누구 명령어"))

