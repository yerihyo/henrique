import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.command.command_entity import CommandEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestSkillEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = CommandEntity.text2entity_list("? 항구 리스본")
        ref = [{'span': (0, 4), 'text': '? 항구', 'value': 'port'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

