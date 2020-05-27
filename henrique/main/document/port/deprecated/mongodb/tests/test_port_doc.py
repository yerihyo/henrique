import logging
from unittest import TestCase

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestPortDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    # def test_01(self):
    #     port_docs = PortDoc.tradegoods2docs_MONGO(["Dashima"])
    #     hyp = smap(PortDoc.doc2key, port_docs)
    #     ref = {'Hanyang', 'Busan', 'Pohang'}
    #
    #     # pprint(hyp)
    #     self.assertEqual(hyp, ref)
