import logging
from pprint import pprint
from unittest import TestCase

from foxylib.tools.collections.collections_tool import smap
from henrique.main.document.port.port_entity import Port, PortEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestPortEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        entity_list = PortEntity.text2entity_list("?시세 초롱 : 말세80ㅎ; 사사리75ㅎ; 시라130ㅅ;")

        hyp = entity_list
        ref = [{'span': (9, 11),
                'text': '말세',
                'type': 'henrique.main.document.port.port_entity.PortEntity',
                'value': 'Marseilles'},
               {'span': (16, 19),
                'text': '사사리',
                'type': 'henrique.main.document.port.port_entity.PortEntity',
                'value': 'Sassari'},
               {'span': (24, 26),
                'text': '시라',
                'type': 'henrique.main.document.port.port_entity.PortEntity',
                'value': 'Syracuse'}]

        # pprint(hyp)
        self.assertEqual(hyp, ref)
