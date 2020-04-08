import logging
from unittest import TestCase

from foxylib.tools.collections.collections_tool import smap
from henrique.main.document.port.port_entity import Port
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestPortEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        ports = Port.tradegood2ports("Dashima")

        hyp = smap(Port.port2codename, ports)
        ref = {'Hanyang', 'Busan', 'Pohang'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)
