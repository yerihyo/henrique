import logging
import os
import sys
from operator import itemgetter as ig

import pytz
import re
from datetime import datetime
from functools import lru_cache
from future.utils import lmap, lfilter

from foxylib.tools.collections.collections_tool import lchain, l_singleton2obj
from foxylib.tools.collections.groupby_tool import gb_tree_global
from foxylib.tools.collections.iter_tool import iter2singleton
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.regex.regex_tool import RegexTool, MatchTool
from foxylib.tools.string.string_tool import str2strip, format_str
from henrique.main.document.culture.culture_entity import CultureEntity
from henrique.main.document.henrique_entity import Entity
from henrique.main.document.port.port import Port
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDict, MarketpriceDoc
from henrique.main.document.price.rate.rate_entity import RateEntity
from henrique.main.document.price.trend.trend_entity import Trend, TrendEntity
from henrique.main.document.server.server import Server
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.datetime.henrique_datetime import HenriqueDatetime
from henrique.main.singleton.khala.henrique_khala import Rowsblock, HenriquePacket
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class Portlike:
    @classmethod
    def entity_types(cls):
        return {PortEntity.entity_type(), CultureEntity.entity_type()}

    @classmethod
    def entity_type2is_portlike(cls, entity_type):
        return entity_type in cls.entity_types()

    @classmethod
    def entity_portlike2port_codenames(cls, entity_portlike):
        entity_type = Entity.entity2type(entity_portlike)
        if entity_type == PortEntity.entity_type():
            return [Entity.entity2value(entity_portlike)]

        if entity_type == CultureEntity.entity_type():
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
            h = {PortEntity.entity_type(): cls.PORTLIKE,
                 CultureEntity.entity_type(): cls.PORTLIKE,
                 TradegoodEntity.entity_type(): cls.TRADEGOOD,
                 RateEntity.entity_type(): cls.RATE,
                 TrendEntity.entity_type(): cls.TREND,
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





class PriceSkill:
    CODENAME = "price"

    @classmethod
    def lang2description(cls, lang):
        from henrique.main.skill.price.price_skill_description import PriceSkillDescription
        return PriceSkillDescription.lang2text(lang)

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
        logger = HenriqueLogger.func_level2logger(cls.price_lang2text, logging.DEBUG)

        if price is None:
            return cls.lang2text_idk(lang)

        rate = MarketpriceDoc.price2rate(price)
        trend = MarketpriceDoc.price2trend(price)
        # raise Exception({"price":price})

        channel_user_codename = MarketpriceDoc.price2channel_user(price)
        channel_user = l_singleton2obj(ChannelUser.codenames2channel_users([channel_user_codename]))
        logger.debug({"price":price, "channel_user":channel_user})

        # raise Exception({"price":price})
        created_at = MarketpriceDoc.price2created_at(price) or MarketpriceDoc.created_at_backoff()
        td = datetime.now(tz=pytz.utc) - created_at
        str_timedelta = HenriqueDatetime.timedelta_lang2str(td, lang)

        arrow = Trend.trend2arrow(trend)
        text_out_base = format_str("{}{} @ {}", str(rate), arrow, str_timedelta)

        if td >= HenriqueDatetime.Constant.TIMEDELTA_OUTDATED:
            return text_out_base

        user_alias = ChannelUser.channel_user2alias(channel_user)
        str_user_alias = "[by {}]".format(user_alias)
        text_out = " ".join([text_out_base, str_user_alias])
        return text_out

    @classmethod
    def packet2rowsblocks(cls, packet):
        from henrique.main.skill.price.price_skill_clique import PriceSkillClique as Clique
        Param = PriceSkillParameter

        text = KhalaPacket.packet2text(packet)
        server_codename = HenriquePacket.packet2server(packet)

        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        config = {Entity.Config.Field.LOCALE: Chatroom.chatroom2locale(chatroom)}
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
            entity_list_tradegood = lfilter(lambda x: Entity.entity2type(x) == TradegoodEntity.entity_type(), entity_list)

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
        price_dict = MarketpriceDict.port_tradegood_iter2price_dict(server_codename, port_tradegood_list)

        # raise Exception({"port_tradegood_list": port_tradegood_list,
        #                  "price_dict": price_dict,
        #                  "groupby_parameter_type": groupby_parameter_type,
        #                  })
        chatroom = Chatroom.codename2chatroom(KhalaPacket.packet2chatroom(packet))
        lang = LocaleTool.locale2lang(Chatroom.chatroom2locale(chatroom))
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
    def blocks2norm_list_for_unittest(cls, blocks):
        def row2header(row):
            match_list = list(cls.pattern_rate_trend().finditer(row))
            match = l_singleton2obj(match_list)
            s,e = MatchTool.match2span(match)
            return str2strip(row[:s])
            # return str2strip(cls.pattern_rate_trend().sub("", row))

        def block2norm_for_unittest(block):
            rows = block.splitlines()
            title = rows[0]

            row_header_list = lmap(row2header, rows[1:])
            return title, row_header_list

        return lmap(block2norm_for_unittest, blocks)

    @classmethod
    def blocks2norm_set_for_unittest(cls, blocks):
        norm_list = cls.blocks2norm_list_for_unittest(blocks)

        return [(title, set(row_header_list))
                for title, row_header_list in norm_list]

# WARMER.warmup()