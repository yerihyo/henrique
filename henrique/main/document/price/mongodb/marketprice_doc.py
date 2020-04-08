from functools import lru_cache
from operator import itemgetter as ig

from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, smap
from foxylib.tools.function.function_tool import FunctionTool

from henrique.main.document.port.mongodb.port_doc import PortDoc
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


class MarketpriceCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("collection", *_, **__)



class MarketpriceDoc:
    class Field:
        CREATED_AT = "created_at"
        PORT = "port"
        TRADEGOOD = "tradegood"
        RATE = "rate"
        TREND = "trend"

        CHATROOM_USER_ID = "chatroom_user_id"
        SERVER = "server"

        @classmethod
        def set(cls):
            return {cls.PORT, cls.TRADEGOOD, cls.RATE, cls.TREND}


    @classmethod
    def key_default(cls, price):
        from henrique.main.document.price.trend.trend_entity import Trend

        rate = cls.price2rate(price)
        v_trend = Trend.trend2int(cls.price2trend(price))

        return -rate, -v_trend

    @classmethod
    def price2port(cls, price):
        return price[cls.Field.PORT]

    @classmethod
    def price2tradegood(cls, price):
        return price[cls.Field.TRADEGOOD]

    @classmethod
    def price2rate(cls, price):
        return price[cls.Field.RATE]

    @classmethod
    def price2trend(cls, price):
        return price[cls.Field.TREND]


class MarketpriceDict:
    @classmethod
    def port_tradegood_iter2price_dict(cls, port_tradegood_iter):
        from henrique.main.document.price.mongodb.markettrend_doc import MarkettrendDoc
        port_tradegood_set = set(port_tradegood_iter)

        port_codenames = smap(ig(0), port_tradegood_set)
        tradegood_codenames = smap(ig(1), port_tradegood_set)

        prices_latest = MarkettrendDoc.ports_tradegoods2price_list_latest(port_codenames, tradegood_codenames)

        price_dict = cls.prices2price_dict(prices_latest)
        return price_dict


    @classmethod
    def prices2price_dict(cls, prices):
        price_list = list(prices)

        def price2key(price):
            port_codename = MarketpriceDoc.price2port(price)
            tradegood_codename = MarketpriceDoc.price2tradegood(price)
            return port_codename, tradegood_codename

        price_dict = merge_dicts([{price2key(price): price} for price in price_list],
                                 vwrite=vwrite_no_duplicate_key)
        return price_dict

    @classmethod
    def lookup(cls, price_dict, port_codename, tradegood_codename):
        return price_dict[(port_codename, tradegood_codename)]

