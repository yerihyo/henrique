from pprint import pprint
from unittest import TestCase

from foxylib.tools.collections.collections_tool import smap
from henrique.main.entity.port.port_entity import PortDoc
from henrique.main.skill.port.port_skill import PortSkill


class TestPortSkill(TestCase):
    def test_01(self):

        j_port_skillnote = PortSkill.str2j_skillnote("?port 리스본")
        j_port_list = PortSkill.j_skillnote2j_port_list(j_port_skillnote)
        hyp = smap(PortDoc.j_port2key, j_port_list)
        ref = {"Lisbon"}

        # pprint({"hyp":hyp})
        self.assertEqual(hyp, ref)