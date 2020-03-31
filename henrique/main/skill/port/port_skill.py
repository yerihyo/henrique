import os
import sys

from functools import partial
from future.utils import lmap
from nose.tools import assert_equals

from foxylib.tools.collections.collections_tool import lchain, smap
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from henrique.main.entity.culture.culture_entity import CultureEntity
from henrique.main.entity.henrique_entity import Entity
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.entity.tradegood.tradegood_entity import TradegoodEntity
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class PortSkill:
    CODENAME = "port"

    @classmethod
    def target_entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity}

    @classmethod
    def _entity_lang2response(cls, entity, lang):
        entity_type = Entity.entity2type(entity)
        codename = Entity.entity2value(entity)

        from henrique.main.skill.port.port_port.port_port_response import PortPortResponse
        from henrique.main.skill.port.port_tradegood.port_tradegood_response import PortTradegoodResponse
        from henrique.main.skill.port.port_culture.port_culture_response import PortCultureResponse

        h_type2func = {PortEntity.TYPE: partial(PortPortResponse.codename_lang2response, lang=lang),
                       TradegoodEntity.TYPE: partial(PortTradegoodResponse.codename_lang2response, lang=lang),
                       CultureEntity.TYPE: partial(PortCultureResponse.codename_lang2response, lang=lang),
                       }

        assert_equals(set(h_type2func.keys()), smap(lambda c: c.TYPE, cls.target_entity_classes()))

        codename2response = h_type2func.get(entity_type)
        if not codename2response:
            raise NotImplementedError("Invalid entity_type: {}".format(entity_type))

        return codename2response(codename)


    @classmethod
    def packet2response(cls, packet):
        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(packet))

        entity_classes = cls.target_entity_classes()
        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE:KhalaPacket.packet2locale(packet)}
        entity_list_raw = lchain(*[c.text2entity_list(text_in, config=config) for c in entity_classes])

        entity_list = sorted(entity_list_raw, key=Entity.entity2span)

        response = "\n\n".join([cls._entity_lang2response(entity, lang) for entity in entity_list])
        return response

