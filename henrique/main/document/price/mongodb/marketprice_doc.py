from datetime import datetime, timedelta
from operator import itemgetter as ig

import pytz
from functools import lru_cache
from future.utils import lmap

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, smap, AbsoluteOrder, \
    lchain, DictTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.document.price.trend.trend_entity import Trend
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


class MarketpriceCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("marketprice", *_, **__)


class MarketpriceDoc:
    class Field:
        CREATED_AT = "created_at"
        PORT = "port"
        TRADEGOOD = "tradegood"
        RATE = "rate"
        TREND = "trend"

        CHANNEL_USER_KEY = "channel_user_key"
        SERVER = "server"

        @classmethod
        def set(cls):
            return {cls.CREATED_AT, cls.PORT, cls.TRADEGOOD, cls.RATE, cls.TREND, cls.CHANNEL_USER_KEY, cls.SERVER}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=200))
    def price_tradegood2doc_fake(cls, port, tradegood):
        rate_fake = 100 + sum(map(len, [port,tradegood])) % 20
        trend_fake = Trend.int2trend(sum(map(len, [port,tradegood])) % 5 - 2)
        created_at_fake = datetime.now(pytz.utc) - timedelta(days=3)
        return {cls.Field.CREATED_AT: created_at_fake,
                cls.Field.PORT: port,
                cls.Field.TRADEGOOD: tradegood,
                cls.Field.RATE: rate_fake,
                cls.Field.TREND: trend_fake,

                }
    @classmethod
    def doc2norm_unittest(cls, doc):
        return DictTool.keys2excluded(doc, [cls.Field.CREATED_AT])


    @classmethod
    def key_default(cls, price):
        from henrique.main.document.price.trend.trend_entity import Trend

        if price is None:
            return AbsoluteOrder.MAX

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

    @classmethod
    def price2created_at(cls, price):
        return price[cls.Field.CREATED_AT]

    @classmethod
    def price2channel_user_key(cls, price):
        return price[cls.Field.CHANNEL_USER_KEY]

    @classmethod
    def ports_tradegoods2price_list_latest(cls, server, port_codenames, tradegood_codenames):
        port_codename_list = list(port_codenames)
        tradegood_codename_list = list(tradegood_codenames)
        # https://stackoverflow.com/a/29368862
        collection = MarketpriceCollection.collection()
        mongo_query = {cls.Field.PORT: {"$in": port_codename_list},
                       cls.Field.TRADEGOOD: {"$in": tradegood_codename_list},
                       cls.Field.SERVER: server,
                       }

        mongo_group_id = {
            "_id": {
                cls.Field.PORT: "${}".format(cls.Field.PORT),
                cls.Field.TRADEGOOD: "${}".format(cls.Field.TRADEGOOD),
            },
        }

        fields_others = cls.Field.set() - {cls.Field.PORT, cls.Field.TRADEGOOD}
        mongo_group_list = lchain([mongo_group_id],
                                  [{field: {"$last": "${}".format(field)}, }
                                   for field in fields_others], )
        mongo_group = merge_dicts(mongo_group_list, vwrite=vwrite_no_duplicate_key)

        mongo_pipeline = [
            {"$match": mongo_query},
            {"$group": mongo_group}
        ]

        def item2doc(item):
            port_codename = JsonTool.down(item, ["_id", cls.Field.PORT])
            tradegood_codename = JsonTool.down(item, ["_id", cls.Field.TRADEGOOD])

            price = merge_dicts([DictTool.keys2filtered(item, fields_others, ),
                                 {cls.Field.PORT: port_codename,
                                  cls.Field.TRADEGOOD: tradegood_codename,
                                  },
                                 ], vwrite=vwrite_no_duplicate_key
                                )

            return price

        item_list = list(collection.aggregate(mongo_pipeline))
        doc_list = lmap(item2doc, item_list)

        return doc_list


class MarketpriceDict:
    @classmethod
    def port_tradegood_iter2price_dict(cls, server, port_tradegood_iter):
        port_tradegood_set = set(port_tradegood_iter)

        port_codenames = smap(ig(0), port_tradegood_set)
        tradegood_codenames = smap(ig(1), port_tradegood_set)

        prices_latest = MarketpriceDoc.ports_tradegoods2price_list_latest(server, port_codenames, tradegood_codenames)

        price_dict = cls.prices2price_dict(prices_latest)
        return price_dict


    @classmethod
    def prices2price_dict(cls, prices):
        price_list = list(prices)

        def price2key(price):
            # raise Exception({"price":price})
            port_codename = MarketpriceDoc.price2port(price)
            tradegood_codename = MarketpriceDoc.price2tradegood(price)
            return port_codename, tradegood_codename

        price_dict = merge_dicts([{price2key(price): price} for price in price_list],
                                 vwrite=vwrite_no_duplicate_key)
        return price_dict

    @classmethod
    def lookup(cls, price_dict, port_codename, tradegood_codename):
        return price_dict.get((port_codename, tradegood_codename))

