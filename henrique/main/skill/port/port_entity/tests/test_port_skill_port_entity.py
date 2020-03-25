import logging
import os
from pprint import pprint
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.port.port_entity.port_skill_port_entity import PortSkillPortEntity


class TestPortSkillPortEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = PortSkillPortEntity.code2response("Lisbon", "ko")
        ref = '[리스본]'

        # pprint(hyp)
        self.assertEqual(hyp, ref)
