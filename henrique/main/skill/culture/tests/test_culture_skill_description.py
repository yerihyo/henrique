from unittest import TestCase

from henrique.main.skill.culture.culture_skill_description import CultureSkillDescription


class TestCultureSkillDescription(TestCase):
    def test_01(self):

        description = CultureSkillDescription.lang2text("ko")

        # pprint({"description":description})
        self.assertTrue(description.startswith("?문화권 명령어"))

