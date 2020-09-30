from pprint import pprint
from unittest import TestCase

from henrique.main.skill.what.what_skill_description import WhatSkillDescription


class TestWhatSkillDescription(TestCase):
    def test_01(self):

        description = WhatSkillDescription.lang2text("ko")

        # pprint(description)
        self.assertTrue(description.startswith("?무엇 명령어"))

