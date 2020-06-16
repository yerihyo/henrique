import logging

import pytz
from datetime import datetime
from future.utils import lmap, lfilter
from itertools import product, chain
from nose.tools import assert_equal

from foxylib.tools.collections.collections_tool import luniq, merge_dicts, vwrite_no_duplicate_key, lchain, \
    l_singleton2obj
from foxylib.tools.collections.iter_tool import iter2singleton, IterTool
from foxylib.tools.native.native_tool import is_none, is_not_none
from foxylib.tools.regex.regex_tool import RegexTool
from foxylib.tools.span.span_tool import SpanTool
from foxylib.tools.string.string_tool import StringTool
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc, MarketpriceCollection
from henrique.main.document.price.rate.rate_entity import RateEntity
from henrique.main.document.price.trend.trend_entity import TrendEntity
from henrique.main.document.server.server import Server
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.khala.henrique_khala import HenriquePacket
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill import PriceSkillParameter, Portlike
from khala.document.packet.packet import KhalaPacket


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
    def entity_classes(cls):
        return {PortEntity, TradegoodEntity, CultureEntity, RateEntity, TrendEntity, }

    @classmethod
    def clique2type(cls, clique):
        has_rate = iter2singleton(map(is_not_none,
                                      [cls.clique2rate(clique),
                                       cls.clique2trend(clique),
                                       ]))

        if has_rate:
            return cls.Type.UPDATE
        return cls.Type.LOOKUP

    @classmethod
    def clique2ports(cls, clique):
        return clique[cls.Field.PORTS]

    @classmethod
    def clique2tradegoods(cls, clique):
        return clique[cls.Field.TRADEGOODS]

    @classmethod
    def clique2rate(cls, clique):
        return clique.get(cls.Field.RATE)

    @classmethod
    def clique2trend(cls, clique):
        return clique.get(cls.Field.TREND)

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

        h = {Param.Type.PORTLIKE: cls.Field.PORTS,
             Param.Type.TRADEGOOD: cls.Field.TRADEGOODS,
             Param.Type.RATE: cls.Field.RATE,
             Param.Type.TREND: cls.Field.TREND,
             }
        return h.get(param_type)

    @classmethod
    def entities_list2clique(cls, entities_list):
        h_list = lmap(cls._entities2dict_part, entities_list)
        # raise Exception({"h_list": h_list, "entities_list": entities_list})
        clique = merge_dicts(h_list, vwrite=vwrite_no_duplicate_key)
        return clique

    @classmethod
    def _entities2dict_part(cls, entities):
        Param = PriceSkillParameter
        param_type = Param.Type.entity_group2parameter_type(entities)
        field = cls.parameter_type2field(param_type)

        if param_type == Param.Type.PORTLIKE:
            port_codenames = lchain(*map(lambda x: Portlike.entity_portlike2port_codenames(x), entities))
            return {field: port_codenames}

        if param_type == Param.Type.TRADEGOOD:
            tradegood_codenames = lmap(Entity.entity2value, entities)
            return {field: tradegood_codenames}

        if param_type == Param.Type.RATE:
            entity = l_singleton2obj(entities)
            rate = Entity.entity2value(entity)
            return {field: rate}

        if param_type == Param.Type.TREND:
            entity = l_singleton2obj(entities)
            trend = Entity.entity2value(entity)
            return {field: trend}

        raise Exception({"param_type":param_type,
                         "entities":entities,
                         })

    @classmethod
    def clique2doc_insert(cls, packet, clique):
        ports = cls.clique2ports(clique)
        tradegoods = cls.clique2tradegoods(clique)
        rate = cls.clique2rate(clique)
        trend = cls.clique2trend(clique)

        port_codename = l_singleton2obj(ports)
        tradegood_codename = l_singleton2obj(tradegoods)

        server_codename = HenriquePacket.packet2server(packet)

        channel_user = KhalaPacket.packet2channel_user(packet)

        doc = {MarketpriceDoc.Field.CREATED_AT: datetime.now(pytz.utc),
               MarketpriceDoc.Field.PORT: port_codename,
               MarketpriceDoc.Field.TRADEGOOD: tradegood_codename,
               MarketpriceDoc.Field.RATE: rate,
               MarketpriceDoc.Field.TREND: trend,

               MarketpriceDoc.Field.SERVER: server_codename,
               MarketpriceDoc.Field.CHANNEL_USER: channel_user,
               }

        return doc

    @classmethod
    def clique_list2update_mongodb(cls, packet, clique_list):
        if not clique_list:
            return None

        doc_list = [cls.clique2doc_insert(packet, clique) for clique in clique_list]
        collection = MarketpriceCollection.collection()
        mongo_result = collection.insert_many(doc_list)
        return mongo_result

    @classmethod
    def entity_group2span(cls, entity_group):
        s1, e1 = Entity.entity2span(entity_group[0])
        s2, e2 = Entity.entity2span(entity_group[-1])
        return s1, e2

    @classmethod
    def text_entities_list2indexes_list(cls, text, entities_list):
        logger = HenriqueLogger.func_level2logger(cls.text_entities_list2indexes_list, logging.DEBUG)

        Param = PriceSkillParameter
        p = len(entities_list)

        param_type_list = lmap(Param.Type.entity_group2parameter_type, entities_list)
        h_param_type2j_latest_series = list(IterTool.iter2dict_value2latest_index_series(param_type_list))
        # logger.debug({"h_param_type2j_latest_series": h_param_type2j_latest_series})

        def j_param_types2j_latest(j, param_types):
            nonlocal h_param_type2j_latest_series

            h_param_type2j_latest = h_param_type2j_latest_series[j]
            return lmap(h_param_type2j_latest.get, param_types)

        def j2valid_portlike_tradegood(j):
            nonlocal entities_list

            j_portlike, j_tradegood = j_param_types2j_latest(j, [Param.Type.PORTLIKE,Param.Type.TRADEGOOD])

            if any(map(is_none, [j_portlike, j_tradegood])):
                return False

            if {j - 1, j} != {j_portlike, j_tradegood}:
                return False

            # span0, span1 = map(cls.entity_group2span, entities_list[j-1:j+1])
            # str_between = StringTool.str_span2substr(text, SpanTool.span_pair2between(span0, span1))
            # if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank(), str_between):
            #     return False

            if j + 1 == p:
                return True

            if Param.Type.entity_group2parameter_type(entities_list[j+1]) == Param.Type.RATE:
                return False

            return True

        def j2valid_trend(j):
            nonlocal entities_list

            if j < 3:
                return False

            j_tuple = j_param_types2j_latest(j, Param.Type.list())
            if any(map(is_none, j_tuple)):
                return False

            entities_tuple = [entities_list[j] if j is not None else None for j in j_tuple]
            if any(map(lambda x: len(x) != 1, entities_tuple)):
                return False

            j_portlike, j_tradegood, j_rate, j_trend = j_tuple
            assert_equal(j_trend, j)
            if j_rate != j-1:
                return False

            if j-2 not in {j_portlike, j_tradegood}:
                return False

            entity_portlike, entity_tradegood, entity_rate, entity_trend = map(l_singleton2obj, entities_tuple)

            if Entity.entity2type(entity_portlike) != PortEntity.entity_type():  # not culture
                return False

            entity_latter = max([entity_portlike, entity_tradegood], key=Entity.entity2span)

            span_latter, span_rate, span_trend = lmap(Entity.entity2span, [entity_latter, entity_rate, entity_trend])

            span_latter_rate = SpanTool.span_pair2between(span_latter, span_rate)
            str_between_latter_rate = StringTool.str_span2substr(text, span_latter_rate)

            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank_or_nullstr(), str_between_latter_rate):
                return False

            span_rate_trend = SpanTool.span_pair2between(span_rate, span_trend)
            str_between_rate_trend = StringTool.str_span2substr(text, span_rate_trend)
            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank_or_nullstr(), str_between_rate_trend):
                return False

            return True

        def j2j_tuple_valid(j):
            nonlocal entities_list

            param_type_this = Param.Type.entity_group2parameter_type(entities_list[j])

            if param_type_this == Param.Type.TREND:
                if not j2valid_trend(j):
                    return None

                j_tuple = j_param_types2j_latest(j, [Param.Type.PORTLIKE, Param.Type.TRADEGOOD, Param.Type.RATE, Param.Type.TREND])
                return sorted(j_tuple)

            if param_type_this in {Param.Type.PORTLIKE, Param.Type.TRADEGOOD}:
                if not j2valid_portlike_tradegood(j):
                    return None

                j_tuple = j_param_types2j_latest(j, [Param.Type.PORTLIKE, Param.Type.TRADEGOOD,])
                return sorted(j_tuple)

            return None

        j_tuples_valid = lfilter(bool, map(j2j_tuple_valid, range(p)))
        logger.debug({"j_tuples_valid":j_tuples_valid})

        # entity_span_list_out = list(SpanTool.spans2nonoverlapping_greedy(valid_entity_spans))

        return j_tuples_valid

    @classmethod
    def entity_pair2is_appendable(cls, text, entity_pair, ):
        Param = PriceSkillParameter

        entity_type_pair = lmap(Entity.entity2type, entity_pair)
        param_type_pair = lmap(Param.Type.entity_type2parameter_type, entity_type_pair)

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
            if cls.entity_pair2is_appendable(text, (entity_list[i - 1], entity_list[i]), ):
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
    def text_entity_list2clique_list(cls, text, entity_list):
        entities_list = cls.entity_list2entities_list_grouped(text, entity_list)

        indexes_clique_list = cls.text_entities_list2indexes_list(text, entities_list)

        # raise Exception({
        #     # "entities_list": entities_list,
        #     "indexes_clique_list": indexes_clique_list,
        #     # "clique_list": clique_list,
        # })

        def indexes2clique(indexes):
            entity_list = lmap(lambda i: entities_list[i], indexes)
            clique = PriceSkillClique.entities_list2clique(entity_list)
            return clique

        clique_list = lmap(indexes2clique, indexes_clique_list)
        return clique_list
