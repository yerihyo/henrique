import os

from functools import lru_cache
from future.utils import lmap

from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.entity.port.mongodb.port_doc import PortDoc
from henrique.main.entity.price.price import PriceDict, Price
from henrique.main.entity.tradegood.mongodb.tradegood_doc import TradegoodDoc
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class MarkettrendCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("markettrend", *_, **__)


class MarkettrendDoc:
    class Field:
        CREATED_AT = "created_at"
        PORT_ID = "port_id"
        TRADEGOOD_ID = "tradegood_id"
        SENDER_NAME = "sender_name"
        SERVER = "server"
        RATE = "rate"
        TREND = "trend"

    @classmethod
    def trend_int2trend_price(cls, v):
        return Price.Trend.Value.list()[v - 1]

    @classmethod
    def ports_tradegoods2prices_latest(cls, port_codenames, tradegood_codenames):
        port_ids = lmap(PortDoc.codename2id, port_codenames)
        tradegood_ids = lmap(TradegoodDoc.codename2id, tradegood_codenames)

        # https://stackoverflow.com/a/29368862
        collection = MarkettrendCollection.collection()
        mongo_query = {cls.Field.PORT_ID: {"$in": port_ids},
                       cls.Field.TRADEGOOD_ID: {"$in": tradegood_ids},
                       }
        mongo_pipeline = [
            {"$match": mongo_query},
            {"$group": {
                "_id": {cls.Field.PORT_ID: "${}".format(cls.Field.PORT_ID),
                        cls.Field.TRADEGOOD_ID: "${}".format(cls.Field.TRADEGOOD_ID),
                        },
                cls.Field.RATE: {"$last": "${}".format(cls.Field.RATE)},
                cls.Field.TREND: {"$last": "${}".format(cls.Field.TREND)},
                cls.Field.SERVER: {"$last": "${}".format(cls.Field.SERVER)},
                cls.Field.CREATED_AT: {"$last": "${}".format(cls.Field.CREATED_AT)},
            }}
        ]

        item_list = list(collection.aggregate(mongo_pipeline))

        def result_item2price(item):
            port_id = JsonTool.down(item, ["_id", cls.Field.PORT_ID])
            tradegood_id = JsonTool.down(item, ["_id", cls.Field.TRADEGOOD_ID])

            price = {Price.Field.PORT: PortDoc.id2codename(port_id),
                     Price.Field.TRADEGOOD: TradegoodDoc.id2codename(tradegood_id),
                     Price.Field.RATE: int(item[cls.Field.RATE]),
                     Price.Field.TREND: cls.trend_int2trend_price(item[cls.Field.TREND]),
                     }
            return price

        return lmap(result_item2price, item_list)

    @classmethod
    def ports_tradegoods2price_dict(cls, port_codenames, tradegood_codenames):
        price_list = cls.ports_tradegoods2prices_latest(port_codenames, tradegood_codenames)
        price_dict = PriceDict.prices2price_dict(price_list)
        return price_dict



    # @classmethod
    # def dict_codename2price_partial(cls):
    #
    #     def doc2price_partial(doc):
    #         langs = ["en", "ko"]
    #
    #         port_partial = {Price.Field.PORT: {lang: cls.doc_lang2names(doc, lang) for lang in langs},
    #                         Price.Field.TRADEGOOD: cls.doc2key(doc)
    #                         }
    #         return port_partial
    #
    #     return merge_dicts([{cls.doc2key(doc): doc2markettrend_partial(doc)}
    #                         for doc in cls.doc_iter_all()],
    #                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
    #                        )
