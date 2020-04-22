from unittest import TestCase

from henrique.main.skill.help.help_skill_description import HelpSkillDescription


class TestHelpSkillDescription(TestCase):
    def test_01(self):

        description = HelpSkillDescription.lang2text("ko")

        # pprint({"description":description})
        self.assertTrue(description.startswith("?도움말 명령어"))

