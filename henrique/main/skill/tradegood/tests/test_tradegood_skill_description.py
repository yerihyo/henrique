from unittest import TestCase

from henrique.main.skill.tradegood.tradegood_skill_description import TradegoodSkillDescription


class TestTradegoodSkillDescription(TestCase):
    def test_01(self):

        description = TradegoodSkillDescription.lang2text("ko")

        # pprint({"description":description})
        self.assertTrue(description.startswith("?교역품 명령어"))
