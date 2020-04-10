import logging
import os
import sys
from operator import itemgetter as ig

import pytz
import re
from datetime import datetime
from functools import lru_cache
from future.utils import lmap, lfilter
from itertools import chain, product
from nose.tools import assert_equal

from foxylib.tools.collections.collections_tool import lchain, l_singleton2obj, merge_dicts, vwrite_no_duplicate_key, \
    luniq
from foxylib.tools.collections.groupby_tool import gb_tree_global
from foxylib.tools.collections.iter_tool import iter2singleton, IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.native.native_tool import is_not_none, is_none
from foxylib.tools.regex.regex_tool import RegexTool, MatchTool
from foxylib.tools.span.span_tool import SpanTool
from foxylib.tools.string.string_tool import StringTool, str2strip, format_str
from henrique.main.document.channel.channel import Channel
from henrique.main.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port import Port
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDict, MarketpriceDoc, MarketpriceCollection
from henrique.main.document.price.rate.rate_entity import RateEntity
from henrique.main.document.price.trend.trend_entity import Trend, TrendEntity
from henrique.main.document.server.server import Server
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.henrique_skill import Rowsblock
from khalalib.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class Portlike:
    @classmethod
    def entity_types(cls):
        return {PortEntity.TYPE, CultureEntity.TYPE}

    @classmethod
    def entity_type2is_portlike(cls, entity_type):
        return entity_type in cls.entity_types()

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
            return iter2singleton(map(cls.entity_type2parameter_type, entity_types))

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_delim(cls):
        return re.compile(r"[,\s]*")

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

        raise Exception(entities)

    @classmethod
    def clique2doc_insert(cls, packet, clique):
        ports = cls.clique2ports(clique)
        tradegoods = cls.clique2tradegoods(clique)
        rate = cls.clique2rate(clique)
        trend = cls.clique2trend(clique)

        port_codename = l_singleton2obj(ports)
        tradegood_codename = l_singleton2obj(tradegoods)
        server = Server.packet2server(packet)

        channel_user_doc = ChannelUserDoc.packet2doc(packet)

        doc = {MarketpriceDoc.Field.CREATED_AT: datetime.now(pytz.utc),
               MarketpriceDoc.Field.PORT: port_codename,
               MarketpriceDoc.Field.TRADEGOOD: tradegood_codename,
               MarketpriceDoc.Field.RATE: rate,
               MarketpriceDoc.Field.TREND: trend,

               MarketpriceDoc.Field.SERVER: server,
               MarketpriceDoc.Field.CHANNEL_USER_KEY: ChannelUserDoc.doc2key(channel_user_doc),
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
    def text_entities_list2entities_spans_clique(cls, text, entities_list):
        Param = PriceSkillParameter
        p = len(entities_list)

        param_type_list = lmap(Param.Type.entity_group2parameter_type, entities_list)
        h_param_type2j_latest_series = list(IterTool.iter2dict_value2latest_index_series(param_type_list))

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

            span0, span1 = map(cls.entity_group2span, entities_list[j-1:j+1])
            str_between = StringTool.str_span2substr(text, SpanTool.span_pair2between(span0, span1))
            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank(), str_between):
                return False

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

            if Entity.entity2type(entity_portlike) != PortEntity.TYPE:  # not culture
                return False

            entity_latter = max([entity_portlike, entity_tradegood], key=Entity.entity2span)

            span_latter, span_rate, span_trend = lmap(Entity.entity2span, [entity_latter, entity_rate, entity_trend])

            span_latter_rate = SpanTool.span_pair2between(span_latter, span_rate)
            str_between_latter_rate = StringTool.str_span2substr(text, span_latter_rate)
            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank(), str_between_latter_rate):
                return False

            span_rate_trend = SpanTool.span_pair2between(span_rate, span_trend)
            str_between_rate_trend = StringTool.str_span2substr(text, span_rate_trend)
            if not RegexTool.pattern_str2match_full(RegexTool.pattern_blank_or_nullstr(), str_between_rate_trend):
                return False

            return True

        def j2valid_entity_span(j):
            nonlocal entities_list

            param_type_this = Param.Type.entity_group2parameter_type(entities_list[j])

            if param_type_this == Param.Type.TREND:
                if j2valid_trend(j):
                    return j-3, j+1

            if param_type_this in {Param.Type.PORTLIKE, Param.Type.TRADEGOOD}:
                if j2valid_portlike_tradegood(j):
                    return j-1, j+1

            return None

        valid_entity_spans = filter(bool, map(j2valid_entity_span, range(p)))
        entity_span_list_out = list(SpanTool.spans2nonoverlapping_greedy(valid_entity_spans))

        return entity_span_list_out

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

        entities_spans_clique = cls.text_entities_list2entities_spans_clique(text, entities_list)
        clique_list = [PriceSkillClique.entities_list2clique(SpanTool.list_span2sublist(entities_list, span))
                       for span in entities_spans_clique]
        return clique_list


class PriceSkill:
    CODENAME = "price"

    @classmethod
    def dict_lang2text_idk(cls):
        return {"ko": "아몰랑",
                "en": "idk",
                }

    @classmethod
    def lang2text_idk(cls, lang):
        raise NotImplementedError()
        # doc = {MarketpriceDoc.Field.}
        # return cls.rate_trend_date_lang2text(100, Trend.Value.AVERAGE)

    @classmethod
    def lang2text_idk_OLD(cls, lang):
        text_idk = cls.dict_lang2text_idk().get(lang)

        if text_idk is None:
            raise NotImplementedError({"lang": lang})

        return text_idk

    # @classmethod
    # def _rate_trend_created_at2text(cls, rate, trend, created_at):
    #     arrow = Trend.trend2arrow(trend)
    #
    #
    #     return format_str("{} {} ({})", str(rate), arrow)

    @classmethod
    def price_lang2text(cls, price, lang):
        if price is None:
            return cls.lang2text_idk(lang)

        rate = MarketpriceDoc.price2rate(price)
        trend = MarketpriceDoc.price2trend(price)
        channel_user_key = MarketpriceDoc.price2channel_user_key(price)
        channel_user = ChannelUserDoc.key2doc(channel_user_key)
        user_ailas = ChannelUserDoc.doc2user_alias(channel_user)

        created_at = MarketpriceDoc.price2created_at(price)

        arrow = Trend.trend2arrow(trend)
        text_out = format_str("{}{} by {}", str(rate), arrow, user_ailas)
        return text_out

    @classmethod
    def packet2rowsblocks(cls, packet):
        Clique = PriceSkillClique
        Param = PriceSkillParameter

        text = KhalaPacket.packet2text(packet)
        server = Server.packet2server(packet)
        config = {Entity.Config.Field.LOCALE: KhalaPacket.packet2locale(packet)}
        entity_list = Entity.text_extractors2entity_list(text, Clique.entity_classes(), config=config)
        clique_list = Clique.text_entity_list2clique_list(text, entity_list)
        clique_list_update = lfilter(lambda x: Clique.clique2type(x) == Clique.Type.UPDATE, clique_list)

        # raise Exception({"entity_list": entity_list,
        #                  "clique_list": clique_list,
        #                  "clique_list_update":clique_list_update,
        #                  })
        if clique_list_update:
            Clique.clique_list2update_mongodb(packet, clique_list_update)

        h_port2indexes = Clique.cliques2dict_port2indexes(clique_list)
        h_tradegood2indexes = Clique.cliques2dict_tradegood2indexes(clique_list)

        def _groupby_paramter_type():
            entity_list_portlike = lfilter(lambda x: Entity.entity2type(x) in Portlike.entity_types(), entity_list)
            entity_list_tradegood = lfilter(lambda x: Entity.entity2type(x) == TradegoodEntity.TYPE, entity_list)

            if not entity_list_portlike:
                return Param.Type.TRADEGOOD

            if not entity_list_tradegood:
                return Param.Type.PORTLIKE

            if len(h_port2indexes) > 1:
                return Param.Type.TRADEGOOD

            if len(h_tradegood2indexes) > 1:
                return Param.Type.PORTLIKE

            span_portlike = Entity.entity2span(entity_list_portlike[0])
            span_tradegood = Entity.entity2span(entity_list_tradegood[0])

            if span_portlike[0] < span_tradegood[0]:
                return Param.Type.PORTLIKE
            else:
                return Param.Type.TRADEGOOD

        groupby_parameter_type = _groupby_paramter_type()

        port_tradegood_list = lchain(*map(Clique.clique2port_tradegood_iter, clique_list))
        price_dict = MarketpriceDict.port_tradegood_iter2price_dict(server, port_tradegood_list)

        # raise Exception({"port_tradegood_list": port_tradegood_list,
        #                  "price_dict": price_dict,
        #                  "groupby_parameter_type": groupby_parameter_type,
        #                  })
        lang = LocaleTool.locale2lang(KhalaPacket.packet2locale(packet))
        block_list = cls.port_tradegood_lists2blocks(port_tradegood_list, price_dict, lang, groupby_parameter_type)
        return block_list

    @classmethod
    def port_tradegood_lists2blocks(cls, port_tradegood_list, price_dict, lang, groupby_parameter_type):
        logger = HenriqueLogger.func_level2logger(cls.port_tradegood_lists2blocks, logging.DEBUG)
        logger.debug({"port_tradegood_list": port_tradegood_list})

        if groupby_parameter_type == PriceSkillParameter.Type.PORTLIKE:
            from henrique.main.skill.price.by_port.price_by_port import PriceByPort

            blocks = [PriceByPort.port2text(port_codename, lmap(ig(1), l), price_dict, lang)
                      for port_codename, l in gb_tree_global(port_tradegood_list, [ig(0)])]
            return blocks

        if groupby_parameter_type == PriceSkillParameter.Type.TRADEGOOD:
            from henrique.main.skill.price.by_tradegood.price_by_tradegood import PriceByTradegood

            blocks = [PriceByTradegood.tradegood2text(tg_codename, lmap(ig(0), l), price_dict, lang)
                      for tg_codename, l in gb_tree_global(port_tradegood_list, [ig(1)])]
            return blocks

        raise Exception(groupby_parameter_type)

    @classmethod
    def packet2response(cls, packet):
        blocks = cls.packet2rowsblocks(packet)
        return Rowsblock.blocks2text(blocks)

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern_rate_trend(cls):
        # rstr_idk = RegexTool.rstr_iter2or(map(re.escape, cls.dict_lang2text_idk().values()))

        rstr_arrows = RegexTool.rstr_iter2or(map(re.escape, Trend.dict_trend2arrow().values()))
        rstr_rate_trend = RegexTool.join(r"", [r"\d{2,3}", rstr_arrows])

        # rstr = r"{}\s*$".format(RegexTool.rstr_iter2or([rstr_idk, rstr_rate_trend]))
        # rstr = r"{}\s*$".format(rstr_rate_trend)

        # raise Exception(rstr)
        pattern = re.compile(RegexTool.rstr2rstr_words(rstr_rate_trend), re.I)
        return pattern

    @classmethod
    def blocks2norm_for_unittest(cls, blocks):
        def row2header(row):
            match_list = list(cls.pattern_rate_trend().finditer(row))
            match = l_singleton2obj(match_list)
            s,e = MatchTool.match2span(match)
            return str2strip(row[:s])
            # return str2strip(cls.pattern_rate_trend().sub("", row))

        def block2norm_for_unittest(block):
            rows = block.splitlines()
            title = rows[0]

            row_headers = set(map(row2header, rows[1:]))
            return title, row_headers

        return lmap(block2norm_for_unittest, blocks)


WARMER.warmup()