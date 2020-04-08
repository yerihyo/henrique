import logging

from psycopg2.sql import Identifier, SQL

from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc
from henrique.main.document.price.trend.trend_entity import Trend
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres


class PortTradegoodStateTable:
    NAME = "unchartedwatersonline_porttradegoodstate"

    @classmethod
    def index_json(cls): return 2

    @classmethod
    def tuple2j(cls, t): return t[cls.index_json()]

    @classmethod
    def tuple2port_name_en(cls, t):
        return JsonTool.down(cls.tuple2j(t), ["market_status","port","name","en"])

    @classmethod
    def tuple2tradegood_name_en(cls, t):
        return JsonTool.down(cls.tuple2j(t), ["market_status", "tradegood", "name", "en"])

    @classmethod
    def tuple2rate(cls, t):
        return JsonTool.down(cls.tuple2j(t), ["market_status", "rate"])

    @classmethod
    def tuple2trend(cls, t):
        trend = JsonTool.down(cls.tuple2j(t), ["market_status", "trend", "value"])
        return trend - 2

    @classmethod
    def marketprice_doc_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.marketprice_doc_iter, logging.DEBUG)

        # h_id2culture = CultureTable.dict_id2codename()
        # logger.debug({"h_id2culture":h_id2culture})

        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT * FROM {} ORDER BY id ASC").format(Identifier(cls.NAME), )
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                port_codename = cls.tuple2port_name_en(t)
                tradegood_codename = cls.tuple2tradegood_name_en(t)
                rate = cls.tuple2rate(t)
                trend = Trend.int2trend(cls.tuple2trend(t))

                data = cls.tuple2j(t)
                server_codename = JsonTool.down(data, ["server"])

                doc = {MarketpriceDoc.Field.PORT: port_codename,
                       MarketpriceDoc.Field.TRADEGOOD: tradegood_codename,
                       MarketpriceDoc.Field.RATE: rate,
                       MarketpriceDoc.Field.TREND: trend,
                       MarketpriceDoc.Field.SERVER: server_codename,
                       # MarketpriceDoc.Field.CHATROOM_USER: channel_user,
                       }
                yield doc
