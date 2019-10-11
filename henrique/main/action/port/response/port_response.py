import os

from foxylib.tools.jinja2.jinja2_tools import Jinja2Toolkit
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.entity.culture.culture_entity import CultureCollection, CultureDocument
from henrique.main.entity.entity import EntityTool
from henrique.main.entity.port.port_entity import PortEntity, PortDocument, PortCollection
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class PortResponse:
    @classmethod
    def port_entity2response(cls, port_entity, j_packet,):
        query = EntityTool.F.entity2text(port_entity)
        j_port = PortEntity.query2j_doc(query)

        j_culture = PortDocument.F.j_port2j_culture(j_port)
        locale = KhalaPacket.j_packet2locale(j_packet)
        lang = LocaleTool.locale2lang(locale)


        filepath = os.path.join(FILE_DIR, "port.response.tmplt.txt")
        j_data = {"port_collection_name":PortCollection.lang2name(lang),
                  "port_name":PortDocument.F.j_port_lang2name(j_port,lang),

                  "culture_collection_name":CultureCollection.lang2name(lang),
                  "culture_name":CultureDocument.F.j_culture_lang2name(j_culture, lang),

                  # "port_status_collection_name":PortStatusCollection.lang2name(lang),
                  # "market_status":None,
                  }
        str_out = Jinja2Toolkit.tmplt_file2str(filepath, j_data)
        return str_out


class CultureResponse:
    @classmethod
    def culture2response(cls, culture):
        pass


class TradegoodResponse:
    @classmethod
    def tradegood2response(cls, tradegood):
        pass
