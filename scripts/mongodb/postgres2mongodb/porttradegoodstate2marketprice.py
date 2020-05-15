import logging
from operator import itemgetter as ig

from datetime import datetime
from foxylib.tools.date.date_tools import DatetimeTool
from functools import lru_cache
from future.utils import lmap, lfilter
from nose.tools import assert_in, assert_true
from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tool import ChunkTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, luniq
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.native.native_tool import is_not_none
from foxylib.tools.string.string_tool import str2lower
from henrique.main.document.port.port import Port
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc, MarketpriceCollection
from henrique.main.document.price.mongodb.markettrend_doc import MarkettrendCollection
from henrique.main.document.price.postgres.porttradegoodstate_table import PortTradegoodStateTable
from henrique.main.document.server.server import Server
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserCollection
from khala.document.channel_user.postgres.chatuser import ChatuserTable


class Porttradegoodstate2Marketprice:
    @classmethod
    def postgres2tuple_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.postgres2tuple_iter, logging.DEBUG)



        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(PortTradegoodStateTable.NAME))
            cursor.execute(sql)
            for t_list_chunk in ChunkTool.chunk_size2chunks(PostgresTool.fetch_iter(cursor), 100000):
                yield from t_list_chunk

                # port_name_en_list = lmap(PortTradegoodStateTable.tuple2port_name_en, t_list_chunk)
                # port_list = name_en_list2port_list(port_name_en_list)
                #
                # tradegood_name_en_list = lmap(PortTradegoodStateTable.tuple2tradegood_name_en, t_list_chunk)
                # tradegood_list = name_en_list2tradegood_list(tradegood_name_en_list)
                #
                # rate_list = lmap(PortTradegoodStateTable.tuple2rate, t_list_chunk)
                # trend_list = lmap(PortTradegoodStateTable.tuple2trend, t_list_chunk)

    @classmethod
    def name2norm(cls, s):
        return s

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_name_en2port(cls):
        return merge_dicts([{cls.name2norm(Port.port_lang2name(port, "en")): port}
                            for port in Port.list_all()],
                           vwrite=vwrite_no_duplicate_key)

    @classmethod
    def name_en2port(cls, name_en):
        return cls._dict_name_en2port()[cls.name2norm(name_en)]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_tradegood_en2port(cls):
        return merge_dicts([{cls.name2norm(Tradegood.tradegood_lang2name(tg, "en")): tg}
                            for tg in Tradegood.list_all()],
                           vwrite=vwrite_no_duplicate_key)

    @classmethod
    def name_en2tradegood(cls, name_en):
        return cls._dict_tradegood_en2port()[cls.name2norm(name_en)]

    @classmethod
    def tuple2pair(cls, t):
        logger = HenriqueLogger.func_level2logger(cls.tuple2pair, logging.DEBUG)

        def chatuser_uuid2channel_user(chatuser_uuid, alias=None):
            if not chatuser_uuid:
                return None

            row = ChatuserTable.uuid2row(chatuser_uuid)
            if not row:
                logger.debug({"chatuser_uuid":chatuser_uuid})
                return None

            channel_user = ChatuserTable.row2channel_user(row, alias=alias)
            return channel_user

        j_postgres = t[PortTradegoodStateTable.index_json()]
        sender_name = j_postgres.get("sender_name")

        created_at = DatetimeTool.fromisoformat(j_postgres["created_at"])

        port_name_en = PortTradegoodStateTable.tuple2port_name_en(t)
        port = cls.name_en2port(port_name_en)

        tradegood_name_en = PortTradegoodStateTable.tuple2tradegood_name_en(t)
        tradegood = cls.name_en2tradegood(tradegood_name_en)

        rate = PortTradegoodStateTable.tuple2rate(t)
        trend = PortTradegoodStateTable.tuple2trend(t)

        chatuser_uuid = PortTradegoodStateTable.tuple2chatuser_uuid(t)
        channel_user = chatuser_uuid2channel_user(chatuser_uuid, alias=sender_name)
        channel_user_code = ChannelUser.channel_user2codename(channel_user) if channel_user else None

        server_alias = str2lower(jdown(j_postgres, ["server", "name"]))
        # logger.debug({"server_alias":server_alias})

        server = Server.alias_lang2server(server_alias, "ko")
        assert_true(server,server_alias)

        marketprice = {MarketpriceDoc.Field.CREATED_AT: created_at,
                       MarketpriceDoc.Field.PORT: Port.port2codename(port),
                       MarketpriceDoc.Field.TRADEGOOD: Tradegood.tradegood2codename(tradegood),
                       MarketpriceDoc.Field.RATE: rate,
                       MarketpriceDoc.Field.TREND: trend,

                       MarketpriceDoc.Field.CHANNEL_USER: channel_user_code,
                       MarketpriceDoc.Field.SERVER: Server.server2codename(server),

                       }

        return marketprice, channel_user

    @classmethod
    def pair_list2mongodb(cls, pair_list):
        logger = HenriqueLogger.func_level2logger(cls.pair_list2mongodb, logging.DEBUG)
        logger.debug({"len(pair_list)": len(pair_list)})

        n = len(pair_list)
        write_concern = WriteConcern(w=3, wtimeout=n)

        def upsert_channel_user():
            channel_user_list_raw = lfilter(is_not_none, map(ig(1), pair_list))
            logger.debug({"len(channel_user_list_raw)": len(channel_user_list_raw)})

            # raise Exception({"channel_user_list_raw[0]": channel_user_list_raw[0]})
            channel_user_list = luniq(channel_user_list_raw, idfun=ChannelUser.channel_user2codename)
            collection = ChannelUserCollection.collection().with_options(write_concern=write_concern)

            def doc2pair(channel_user):
                cond = {ChannelUser.Field.CODENAME: ChannelUser.channel_user2codename(channel_user)}
                return cond, channel_user

            j_pair_list = lmap(doc2pair, channel_user_list)
            MongoDBTool.j_pair_list2upsert(collection, j_pair_list)

        def upsert_marketprice():
            marketprice_list = lmap(ig(0), pair_list)
            collection = MarketpriceCollection.collection().with_options(write_concern=write_concern)
            j_pair_list = [(x,x) for x in marketprice_list]
            MongoDBTool.j_pair_list2upsert(collection, j_pair_list)

        upsert_channel_user()
        upsert_marketprice()



    @classmethod
    def all(cls):
        tuple_iter = cls.postgres2tuple_iter()
        pair_iter = map(cls.tuple2pair, tuple_iter)

        for pair_list in ChunkTool.chunk_size2chunks(pair_iter, 1000):
            cls.pair_list2mongodb(pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    Porttradegoodstate2Marketprice.all()

if __name__ == "__main__":
    main()
