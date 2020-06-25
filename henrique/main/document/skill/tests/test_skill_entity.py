import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.henrique_entity import HenriqueEntity
from henrique.main.document.skill.skill_entity import SkillEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestSkillEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = SkillEntity.text2entity_list("? 항구 리스본", config=config)
        ref = [{'span': (2, 4),
                'text': '항구',
                'type': 'henrique.main.document.skill.skill_entity.SkillEntity',
                'value': 'port'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_02(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = SkillEntity.text2entity_list("? ㅆ 리스본", config=config)
        ref = [{'span': (2, 3),
                'text': 'ㅆ',
                'type': 'henrique.main.document.skill.skill_entity.SkillEntity',
                'value': 'price'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

    def test_03(self):
        config = {HenriqueEntity.Config.Field.LOCALE: "ko-KR"}
        hyp = SkillEntity.text2entity_list("? 도움말 항구", config=config)
        ref = [{'span': (2, 5),
                'text': '도움말',
                'type': 'henrique.main.document.skill.skill_entity.SkillEntity',
                'value': 'help'},
               {'span': (6, 8),
                'text': '항구',
                'type': 'henrique.main.document.skill.skill_entity.SkillEntity',
                'value': 'port'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)
