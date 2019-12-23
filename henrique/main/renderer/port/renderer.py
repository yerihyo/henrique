import os

from foxylib.tools.jinja2.jinja2_tool import Jinja2Tool
from henrique.main.action.port.port_action import PortSpell, PortAnswer
from henrique.main.entity.port.port_entity import PortDoc
from henrique.main.entity.port.port_reference import PortReference

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class PortRenderer:
    @classmethod
    def j_port2str(cls, j_port, lang, ):
        filepath = os.path.join(FILE_DIR, "port.tmplt.txt")
        j_data = {"port_typename": PortReference.lang2name(lang),
                  "port_name": PortDoc.j_port_lang2name(j_port, lang),

                  "culture_collection_name": "n/a",  # CultureCollection.lang2name(lang),
                  "culture_name": "n/a",  # CultureDocument.F.j_culture_lang2name(j_culture, lang),

                  "port_status_collection_name": "n/a",  # PortStatusCollection.lang2name(lang),
                  "port_status": "n/a",  # None,
                  }
        str_out = Jinja2Tool.tmplt_file2str(filepath, j_data)
        return str_out

    @classmethod
    def j_answer2str(cls, j_answer, lang):
        spell = PortAnswer.j_answer2spell(j_answer)
        j_port_list = PortAnswer.j_answer2j_port_list(j_answer)

        str_port_list = [cls.j_port2str(j_port, lang)
                         for j_port in j_port_list]

        filepath = os.path.join(FILE_DIR, "answer.tmplt.txt")
        j_body = {"spell":spell,
                  "str_ports":"\n\n".join(str_port_list),
                  }
        str_out = Jinja2Tool.tmplt_file2str(filepath, j_body)
        return str_out

    @classmethod
    def spell_lang2str(cls, spell, lang):
        j_answer = PortSpell.str2j_answer(spell)
        return cls.j_answer2str(j_answer, lang)
