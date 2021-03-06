import logging
from pprint import pprint
from unittest import TestCase

from henrique.main.document.server.server_entity import ServerEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestServerEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        hyp = ServerEntity.text2entity_list("Maris 글섭")
        ref = [{'span': (0, 5), 'text': 'Maris', 'type': ServerEntity.entity_type(), 'value': 'maris'},
               {'span': (6, 8), 'text': '글섭', 'type': ServerEntity.entity_type(), 'value': 'maris'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)

