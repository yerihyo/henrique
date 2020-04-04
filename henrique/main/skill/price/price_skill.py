import os
import sys

from future.utils import lmap, lfilter
from nose.tools import assert_true

from foxylib.tools.collections.collections_tool import lchain, l_singleton2obj
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.entity.culture.culture_entity import CultureEntity
from henrique.main.entity.henrique_entity import Entity
from henrique.main.entity.port.port import Port
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.entity.price.marketprice import MarketpriceDict, Marketprice
from henrique.main.entity.price.trend.trend_entity import Trend
from henrique.main.entity.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.skill.henrique_skill import Rowsblock
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class Portlike:
    @classmethod
    def entity_type2is_portlike(cls, entity_type):
        return entity_type in {PortEntity.TYPE, CultureEntity.TYPE}

    @classmethod
    def entity_portlike2port_codenames(cls, entity_portlike):
        entity_type = Entity.entity2type(entity_portlike)
        if entity_type == PortEntity.TYPE:
            return [Entity.entity2value(entity_portlike)]

        if entity_type == CultureEntity.TYPE:
            culture_codename = Entity.entity2value(entity_portlike)
            port_list = Port.culture2ports(culture_codename)
            return lmap(Port.port2codename, port_list)

        raise RuntimeError({"entity_type": entity_type})


class PriceSkill:
    CODENAME = "price"



    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity}

    @classmethod
    def price_lang2text(cls, price, lang):
        rate = Marketprice.price2rate(price)
        trend = Marketprice.price2trend(price)
        arrow = Trend.trend2arrow(trend)

        return " ".join([str(rate), arrow])

    @classmethod
    def packet2rowsblocks(cls, packet):
        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(packet))

        entity_classes = cls.target_entity_classes()
        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE: KhalaPacket.packet2locale(packet)}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=Entity.entity2span)

        entity_list_portlike = lfilter(lambda x: Portlike.entity_type2is_portlike(Entity.entity2type(x)), entity_list)
        entity_list_tradegood = lfilter(lambda x: Entity.entity2type(x) in {TradegoodEntity.TYPE, }, entity_list)

        assert_true(entity_list_portlike)
        assert_true(entity_list_tradegood)

        port_codename_list = lchain(*map(Portlike.entity_portlike2port_codenames, entity_list_portlike))
        tradegood_codename_list = lmap(Entity.entity2value, entity_list_tradegood)
        price_dict = MarketpriceDict.ports_tradegoods2price_dict(port_codename_list, tradegood_codename_list)

        def codename_lists2rowsblocks(_port_codename_list, _tradegood_codename_list):
            if len(_port_codename_list) == 1:
                port_codename = l_singleton2obj(_port_codename_list)
                from henrique.main.skill.price.by_port.price_by_port import PriceByPort
                return [PriceByPort.port2text(port_codename, _tradegood_codename_list, price_dict, lang)]

            from henrique.main.skill.price.by_tradegood.price_by_tradegood import PriceByTradegood
            blocks = [PriceByTradegood.tradegood2text(tg_codename, _port_codename_list, price_dict, lang)
                      for tg_codename in _tradegood_codename_list]
            return blocks

        blocks = codename_lists2rowsblocks(port_codename_list, tradegood_codename_list)
        return blocks

    @classmethod
    def packet2response(cls, packet):
        blocks = cls.packet2rowsblocks(packet)
        return Rowsblock.blocks2text(blocks)

    @classmethod
    def blocks2norm_for_unittest(cls, blocks):
        def block2norm_for_unittest(block):
            rows = block.splitlines()
            title = rows[0]
            row_headers = set(" ".join(row.split()[:-2]) for row in rows[1:])
            return title, row_headers

        return lmap(block2norm_for_unittest, blocks)

# @classmethod
    # @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    # @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    # def j_yaml(cls):
    #     filepath = os.path.join(FILE_DIR, "action.yaml")
    #     return YAMLTool.filepath2j(filepath)
    #
    # @classmethod
    # def respond(cls, packet):
    #     from henrique.main.entity.tradegood.subaction.tradegood_subactions import TradegoodTradegoodSubaction
    #
    #     text = KhalaPacket.packet2text(packet)
    #
    #     tradegood_entity_list = TradegoodEntity.text2entity_list(text)
    #
    #     str_list = lmap(lambda p:TradegoodTradegoodSubaction.tradegood_entity2response(p,packet), tradegood_entity_list)
    #
    #     str_out = "\n\n".join(str_list)
    #
    #     return KhalaResponse.Builder.str2j_response(str_out)

WARMER.warmup()