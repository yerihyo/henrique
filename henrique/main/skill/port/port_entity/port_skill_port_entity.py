import os

from foxylib.tools.entity.entity_tool import Entity
from foxylib.tools.jinja2.jinja2_tool import Jinja2Renderer
from henrique.main.entity.port.port_entity import PortDoc

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class PortSkillPortEntity:
    @classmethod
    def entity2response(cls, port_entity, lang):

        port_key = Entity.entity2value(port_entity)
        port_doc = PortDoc.key2doc(port_key)

        filepath = os.path.join(FILE_DIR, "tmplt.{}.part.txt".format(lang))

        data = {"name": PortDoc.doc_lang2name(port_doc, lang)}
        text_out = Jinja2Renderer.textfile2text(filepath, data)

        return text_out

