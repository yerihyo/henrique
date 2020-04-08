import copy
import os
from itertools import chain, product

import re
import sys
from collections import defaultdict
from functools import lru_cache

from future.utils import lmap, lfilter
from nose.tools import assert_true, assert_equal

from foxylib.tools.collections.collections_tool import lchain, l_singleton2obj, merge_dicts, vwrite_no_duplicate_key, \
    luniq
from foxylib.tools.collections.iter_tool import iter2singleton, IterTool
from foxylib.tools.compare.minimax_tool import minimax
from foxylib.tools.coroutine.coro_tool import CoroTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.span.span_tool import SpanTool
from foxylib.tools.string.string_tool import StringTool
from henrique.main.entity.culture.culture_entity import CultureEntity
from henrique.main.entity.henrique_entity import Entity
from henrique.main.entity.port.port import Port
from henrique.main.entity.port.port_entity import PortEntity
from henrique.main.entity.price.marketprice import MarketpriceDict, Marketprice
from henrique.main.entity.price.rate.rate_entity import RateEntity
from henrique.main.entity.price.trend.trend_entity import Trend, TrendEntity
from henrique.main.entity.tradegood.tradegood import Tradegood
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

class PriceSkillBlock:
    pass

# class PriceSkillPacketdata:
#     def __init__(self, text, locale):
#         self.text = text
#         self.locale = locale
#
#     @classmethod
#     def entity_classes(cls):
#         return {PortEntity, TradegoodEntity, CultureEntity, RateEntity, TrendEntity, }
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def entity_list(self):
#         cls = self.__class__
#         config = {Entity.Config.Field.LOCALE: self.locale}
#         return lchain(*[c.text2entity_list(self.text, config=config) for c in cls.entity_classes()])
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def entity_span_list(self):
#         entity_list = self.entity_list()
#         entity_type_list = lmap(Entity.entity2type, entity_list)
#         parameter_type_list = lmap(PriceSkillParameterType.entity_type2parameter_type, entity_type_list)
#         return list(PriceSkillParameterType.types2spans(parameter_type_list))
#
#     def _parameter_type2entity_span_latest_list(self):
#         entity_list = self.entity_list()
#         entity_span_list = self.entity_span_list()
#
#         n, p = len(entity_list), len(entity_span_list)

class PriceSkillParameter:
    class Type:
        PORTLIKE = "portlike"
        TRADEGOOD = "tradegood"
        RATE = "rate"
        TREND = "trend"

        @classmethod
        def list(cls): return [cls.PORTLIKE, cls.TRADEGOOD, cls.RATE, cls.TREND, ]

        @classmethod
        def entity_type2parameter_type(cls, entity_type):
            h = {PortEntity.TYPE: cls.PORTLIKE,
                 CultureEntity.TYPE: cls.PORTLIKE,
                 TradegoodEntity.TYPE: cls.TRADEGOOD,
                 RateEntity.TYPE: cls.RATE,
                 TrendEntity.TYPE: cls.TREND,
                 }

            return h.get(entity_type)

        @classmethod
        def entity_group2parameter_type(cls, entity_list):
            entity_types = map(Entity.entity2type, entity_list)
            return iter2singleton(map(cls.entity_type2parameter_type,entity_types))

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_delim(cls):
        return re.compile(r"[,\s]+")

    @classmethod
    def text2is_delim(cls, text):
        return RegexTool.pattern_str2match_full(cls.pattern_delim(), text)




class PriceSkillClique:
    class Field:
        PORTS = "ports"
        TRADEGOODS = "tradegoods"
        RATE = "rate"
        TREND = "trend"

    class Type:
        UPDATE = "update"
        LOOKUP = "lookup"

    @classmethod
    def clique2ports(cls, clique):
        return clique[cls.Field.PORTS]

    @classmethod
    def clique2tradegoods(cls, clique):
        return clique[cls.Field.TRADEGOODS]

    @classmethod
    def clique2port_tradegood_iter(cls, clique):
        ports = cls.clique2ports(clique)
        tradegoods = cls.clique2tradegoods(clique)
        return product(ports, tradegoods)

    @classmethod
    def cliques2dict_port2indexes(cls, clique_list):
        port_codename_list = luniq(chain(*map(cls.clique2ports, clique_list)))
        h_port2index = {p:i for i,p in enumerate(port_codename_list)}
        return h_port2index

    @classmethod
    def cliques2dict_tradegood2indexes(cls, clique_list):
        tradegood_codename_list = luniq(chain(*map(cls.clique2tradegoods, clique_list)))
        h_tg2index = {tg: i for i, tg in enumerate(tradegood_codename_list)}
        return h_tg2index

    @classmethod
    def parameter_type2field(cls, param_type):
        Param = PriceSkillParameter

        h = {Param.Type.PORTLIKE:cls.Field.PORTS,
             Param.Type.TRADEGOOD: cls.Field.TRADEGOODS,
             Param.Type.RATE: cls.Field.RATE,
             Param.Type.TREND: cls.Field.TREND,
             }
        return h.get(param_type)

    @classmethod
    def entities_list2clique(cls, entities_list):
        h_list = lmap(cls._entities2dict_part, entities_list)
        clique = merge_dicts(h_list, vwrite=vwrite_no_duplicate_key)
        return clique

    @classmethod
    def _entities2dict_part(cls, entities):
        Param = PriceSkillParameter
        param_type = Param.Type.entity_group2parameter_type(entities)
        field = cls.parameter_type2field(param_type)

        if field == cls.Field.PORTS:
            port_list = lmap(lambda x: Port.codename2port(Portlike.entity_portlike2port_codenames(x)), entities)
            return {field:port_list}

        if field == cls.Field.TRADEGOODS:
            tradegood_list = lmap(lambda x: Tradegood.codename2tradegood(Entity.entity2value(x)), entities)
            return {field: tradegood_list}

        if field == cls.Field.RATE:
            entity = l_singleton2obj(entities)
            rate = Entity.entity2value(entity)
            return {field: rate}

        if field == cls.Field.TREND:
            entity = l_singleton2obj(entities)
            trend = Entity.entity2value(entity)
            return {field: trend}

        raise Exception(entities)



class PriceSkill:
    CODENAME = "price"

    @classmethod
    def entity_group2span(cls, entity_group):
        s1, e1 = Entity.entity2span(entity_group[0])
        s2, e2 = Entity.entity2span(entity_group[1])
        return s1, e2

    @classmethod
    def text_entities_list2is_contiguous(cls, text, entities_list):
        n = len(entities_list)
        span_list = lmap(cls.entity_group2span, entities_list)

        for i in range(1, n):
            str_between = StringTool.str_span2substr(text, SpanTool.span_pair2between(span_list[i - 1], span_list[i]))
            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank(), str_between):
                return False

        return True


    @classmethod
    def text_entities_list2entities_spans_clique(cls, text, entities_list):
        Param = PriceSkillParameter
        p = len(entities_list)

        param_type_list = lmap(Param.Type.entity_group2parameter_type, entities_list)
        h_param_type2j_latest_list = list(IterTool.iter2dict_value2latest_index_iter(param_type_list))

        def j_param_types2j_latest(j, param_types):
            nonlocal h_param_type2j_latest_list

            h_param_type2j_latest = h_param_type2j_latest_list[j]
            return lmap(h_param_type2j_latest.get, param_types)

        def j2valid_portlike_tradegood(j):
            nonlocal entities_list

            j_portlike, j_tradegood = j_param_types2j_latest(j, [Param.Type.PORTLIKE,Param.Type.TRADEGOOD])

            if not all([j_portlike, j_tradegood]):
                return False

            if {j - 1, j} != {j_portlike, j_tradegood}:
                return False

            entities_pair = SpanTool.list_span2sublist(entities_list, (j - 1, j))
            if not cls.text_entities_list2is_contiguous(text, entities_pair):
                return False

            if j + 1 == p:
                return True

            if Param.Type.entity_group2parameter_type(entities_list[j+1]) == Param.Type.TREND:
                return False

            return True

        def j2valid_trend(j):
            nonlocal entities_list

            if j < 3:
                return False

            j_tuple = j_param_types2j_latest(j, Param.Type.list())
            if not all(j_tuple):
                return False

            entities_tuple = [entities_list[j] if j is not None else None for j in j_tuple]
            if not all(map(lambda x: len(x) == 1, entities_tuple)):
                return False

            j_portlike, j_tradegood, j_rate, j_trend = j_tuple
            assert_equal(j_trend, j)
            if j_rate != j-1:
                return False

            if j-2 not in {j_portlike, j_tradegood}:
                return False

            entity_portlike, entity_tradegood, entity_rate, entity_trend = map(l_singleton2obj, entities_tuple)

            if Entity.entity2type(entity_portlike) != PortEntity.TYPE:  # not culture
                return False

            entity_latter = max([entity_portlike, entity_tradegood], key=Entity.entity2span)

            entities_list = [entity_latter, entity_rate, entity_trend]
            if not cls.text_entities_list2is_contiguous(text, entities_list):
                return False

            return True

        def j2valid_entity_span(j):
            nonlocal entities_list

            param_type_this = Param.Type.entity_group2parameter_type(entities_list[j])

            if param_type_this == Param.Type.TREND:
                if j2valid_trend(j):
                    return j-3, j

            if param_type_this in {Param.Type.PORTLIKE, Param.Type.TRADEGOOD}:
                if j2valid_portlike_tradegood(j):
                    return j-1, j

            return None

        valid_entity_spans = filter(bool, map(j2valid_entity_span, range(p)))
        entity_span_list_out = list(SpanTool.spans2nonoverlapping_greedy(valid_entity_spans))

        return entity_span_list_out

    @classmethod
    def text_entities_list2clique_list(cls, text, entities_list):
        entities_spans_clique = cls.text_entities_list2entities_spans_clique(text, entities_list)
        clique_list = [PriceSkillClique.entities_list2clique(SpanTool.list_span2sublist(entities_list, span))
                       for span in entities_spans_clique]
        return clique_list

    @classmethod
    def price_lang2text(cls, price, lang):
        rate = Marketprice.price2rate(price)
        trend = Marketprice.price2trend(price)
        arrow = Trend.trend2arrow(trend)

        return " ".join([str(rate), arrow])



    # @classmethod
    # def text_entity_list2valid_tuples(cls, text, entity_list_in,):
    #     entity_list_sorted = sorted(entity_list_in, key=Entity.entity2span)
    #
    #
    #     # index_tuples_portlike, index_tuples_tradegood, index_tuples_rate, index_tuples_trend = [], [], [], []
    #     n = len(entity_list_sorted)
    #
    #
    #
    #
    #
    #
    #     def indexes2uptodate(indexes_target, indexes_base):
    #         if not indexes_target:
    #             return False
    #
    #         return indexes_target[0] > indexes_base[-1]
    #
    #     def index2valid_parameters(index, h_parameter_type2indexes):
    #         entity = entity_list_sorted[index]
    #         entity_type = Entity.entity2type(entity)
    #         parameter_type = cls.ParameterType.entity_type2parameter_type(entity_type)
    #
    #         if parameter_type not in {cls.ParameterType.PORTLIKE, cls.ParameterType.TRADEGOOD}:
    #             return None
    #
    #         indexes_portlike = h_parameter_type2indexes.get(cls.ParameterType.PORTLIKE)
    #         indexes_tradegood = h_parameter_type2indexes.get(cls.ParameterType.TRADEGOOD)
    #         indexes_rate = h_parameter_type2indexes.get(cls.ParameterType.RATE)
    #         indexes_trend = h_parameter_type2indexes.get(cls.ParameterType.TREND)
    #
    #         if not indexes_portlike:
    #             return None
    #
    #         if not indexes_tradegood:
    #             return None
    #
    #         is_rate_uptodate = all([indexes2uptodate(indexes_rate, indexes_portlike),
    #                                 indexes2uptodate(indexes_rate, indexes_tradegood),
    #                                 ])
    #
    #         is_trend_uptodate = all([indexes2uptodate(indexes_trend, indexes_portlike),
    #                                  indexes2uptodate(indexes_trend, indexes_tradegood),
    #                                  ])
    #
    #     h_parameter_type2indexes_latest = defaultdict(list)
    #
    #     for i in range(n):
    #         entity = entity_list_sorted[i]
    #         parameter_type = cls.ParameterType.entity_type2parameter_type(Entity.entity2type(entity))
    #
    #         indexes_list = h_parameter_type2indexes_list.get(parameter_type)
    #         if indexes_list and indexes_list[-1][-1] == i-1:
    #             indexes_list[-1].append(i)
    #         else:
    #             indexes_list.append([i])

    @classmethod
    def entity_pair2is_appendable(cls, text, entity_pair, ):
        Param = PriceSkillParameter

        param_type_pair = lmap(Param.Type.entity_type2parameter_type, entity_pair)
        for param_type in param_type_pair:
            if param_type not in {Param.Type.PORTLIKE, Param.Type.TRADEGOOD}:
                return False

        param_type_1, param_type_2 = param_type_pair
        if param_type_1 != param_type_2:
            return False

        span_pair = lmap(Entity.entity2span, entity_pair)
        text_between = StringTool.str_span2substr(text, SpanTool.span_pair2between(*span_pair))
        is_fullmatch = RegexTool.pattern_str2match_full(Param.pattern_delim(), text_between)
        if not is_fullmatch:
            return False

        return True

    @classmethod
    def entity_list2group_spans(cls, text, entity_list):
        n = len(entity_list)

        i_last = 0
        for i in range(1, n):
            if cls.entity_pair2is_appendable(text, (entity_list[i-1], entity_list[i]), ):
                continue

            yield (i_last, i)
            i_last = i

        if n > i_last:
            yield (i_last, n)

    @classmethod
    def entity_list2entities_list_grouped(cls, text, entity_list):
        return [SpanTool.list_span2sublist(entity_list, span)
                for span in cls.entity_list2group_spans(text, entity_list)]

    @classmethod
    def entities2has_rate_entity(cls):
    @classmethod
    def entities_list2update_mongodb(cls, entities_list):
        raise NotImplementedError()

    @classmethod
    def packet2rowsblocks(cls, packet):
        Clique = PriceSkillClique

        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(packet))

        entity_classes = {PortEntity, TradegoodEntity, CultureEntity, RateEntity, TrendEntity, }
        text_in = KhalaPacket.packet2text(packet)
        config = {Entity.Config.Field.LOCALE: KhalaPacket.packet2locale(packet)}
        entity_list = sorted(chain(*[c.text2entity_list(text_in, config=config) for c in entity_classes]),
                             key=Entity.entity2span)

        entities_list = cls.entity_list2entities_list_grouped(text_in, entity_list)
        clique_list = cls.text_entities_list2clique_list(text_in, entities_list)

        clique_list_update = lfilter(lambda x: Clique.clique2type(x) == Clique.Type.UPDATE, clique_list)

        h_port2indexes = Clique.cliques2dict_port2indexes(clique_list)
        h_tradegood2indexes = Clique.cliques2dict_tradegood2indexes(clique_list)

        is_port_grouped = len(h_port2indexes) == 1 or len(h_tradegood2indexes)>1

        def port_tradegood2key_sort(port_codename, tradegood_codename):
            port_index = h_port2indexes[port_codename]
            tradegood_index = h_tradegood2indexes[tradegood_codename]

            if is_port_grouped:
                return port_index, tradegood_index
            else:
                return tradegood_index, port_index

        port_tradegood_list = sorted(chain(*map(Clique.clique2port_tradegood_iter, clique_list)),
                                     key=lambda ptg: port_tradegood2key_sort(*ptg))
        MarketpriceDict.ports_tradegoods2price_dict()

        if is_port_grouped:
            from henrique.main.skill.price.by_port.price_by_port import PriceByPort
            PriceByPort.port2text()

        entities_list_for_update = lfilter(cls.entities2has_rate, entities_list_valid)



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