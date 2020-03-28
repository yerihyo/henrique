import logging
from pprint import pprint
from unittest import TestCase

from foxylib.tools.collections.collections_tool import smap

from henrique.main.entity.port.port_entity import PortDoc
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestPortEntity(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        port_docs = PortDoc.tradegoods2docs_MONGO(["Dashima"])
        hyp = smap(PortDoc.doc2codename, port_docs)
        ref = {'Hanyang', 'Busan', 'Pohang'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)


    def test_02(self):
        ports = PortDoc.tradegood2docs("Dashima")
        hyp = smap(PortDoc.doc2codename, ports)
        ref = {'Hanyang', 'Busan', 'Pohang'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)
