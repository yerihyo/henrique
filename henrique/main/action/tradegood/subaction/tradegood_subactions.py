import os

from foxylib.tools.jinja2.jinja2_tools import Jinja2Toolkit
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.hub.entity.entity_tool import EntityTool
from henrique.main.action.tradegood.tradegood_entity import TradegoodEntity, TradegoodDocument, TradegoodCollection
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class TradegoodTradegoodSubaction:
    @classmethod
    def tradegood_entity2response(cls, tg_entity, j_packet,):
        query = EntityTool.F.entity2text(tg_entity)
        j_tradegood = TradegoodEntity.query2j_doc(query)

        #j_culture = TradegoodDocument.F.j_tradegood2j_culture(j_tradegood)
        locale = KhalaPacket.j_packet2locale(j_packet)
        lang = LocaleTool.locale2lang(locale)


        filepath = os.path.join(FILE_DIR, "tradegood.tradegood.tmplt.txt")
        j_data = {"tradegood_collection_name":TradegoodCollection.lang2name(lang),
                  "tradegood_name":TradegoodDocument.j_tradegood_lang2name(j_tradegood,lang),

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
