import logging

from datetime import datetime
from future.utils import lmap
from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tool import ChunkTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.string.string_tool import str2lower
from henrique.main.entity.markettrend.trend_entity import PortTradegoodStateTable, MarkettrendCollection, \
    MarkettrendDocument
from henrique.main.entity.port.port_entity import PortDoc
from henrique.main.entity.tradegood.tradegood_entity import TradegoodDoc
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres


class Markettrend2MongoDB:



    @classmethod
    def postgres2j_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.postgres2j_iter, logging.DEBUG)

        def name_en_list2j_port_list(name_en_list):
            norm = str2lower

            h = merge_dicts([{norm(PortDoc.doc_lang2name(doc, "en")): doc}
                             for doc in PortDoc.doc_list_all()],
                            vwrite=vwrite_no_duplicate_key)

            doc_list = [h.get(norm(x)) for x in name_en_list]
            return doc_list

        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(PortTradegoodStateTable.NAME))
            cursor.execute(sql)
            for t_list_chunk in ChunkTool.chunk_size2chunks(PostgresTool.fetch_iter(cursor), 100000):

                port_name_en_list = lmap(PortTradegoodStateTable.tuple2port_name_en, t_list_chunk)
                j_port_list = name_en_list2j_port_list(port_name_en_list)

                tradegood_name_en_list = lmap(PortTradegoodStateTable.tuple2tradegood_name_en, t_list_chunk)
                tradegood_id_list = TradegoodDoc.name_en_list2doc_id_list(tradegood_name_en_list)

                rate_list = lmap(PortTradegoodStateTable.tuple2rate, t_list_chunk)
                trend_list = lmap(PortTradegoodStateTable.tuple2trend, t_list_chunk)

                def tuple2j_doc(t,i):
                    j_postgres = t[PortTradegoodStateTable.index_json()]
                    sender_name = j_postgres.get("sender_name")

                    j_doc = {MarkettrendDocument.F.SERVER: jdown(j_postgres, ["server","name"]),
                             MarkettrendDocument.F.CREATED_AT: datetime.fromisoformat(j_postgres["created_at"]),
                             MarkettrendDocument.F.PORT_ID: MongoDBTool.j_doc2id(j_port_list[i]),
                             MarkettrendDocument.F.TRADEGOOD_ID: tradegood_id_list[i],
                             MarkettrendDocument.F.RATE: rate_list[i],
                             MarkettrendDocument.F.TREND: trend_list[i],
                             }

                    if sender_name:
                        j_doc[MarkettrendDocument.F.SENDER_NAME] = sender_name

                    return j_doc

                j_doc_list_chunk = [tuple2j_doc(t, i) for i, t in enumerate(t_list_chunk)]
                yield from j_doc_list_chunk

    @classmethod
    def j_iter2mongodb(cls, j_iter, chunk_size = 100000):
        logger = HenriqueLogger.func_level2logger(cls.j_iter2mongodb, logging.DEBUG)
        j_list = list(j_iter)
        n = len(j_list)
        logger.debug({"n":n})


        write_concern = WriteConcern(w=3, wtimeout=chunk_size)
        collection = MarkettrendCollection.collection(write_concern=write_concern)

        for i, j_list_chunk in enumerate(ChunkTool.chunk_size2chunks(j_list, chunk_size)):
            logger.debug({"i/n": "{}/{}".format(i*chunk_size, n)})
            j_pair_list = [(j,j) for j in j_list_chunk]
            MongoDBTool.j_pair_iter2upsert(collection, j_pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    j_list = list(Markettrend2MongoDB.postgres2j_iter())
    logger.debug({"# j_list":len(j_list)})

    Markettrend2MongoDB.j_iter2mongodb(j_list)

if __name__ == "__main__":
    main()