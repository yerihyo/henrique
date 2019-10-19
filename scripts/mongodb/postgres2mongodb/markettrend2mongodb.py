import logging
from datetime import datetime

from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tools import ChunkToolkit
from foxylib.tools.collections.collections_tools import luniq, lchain
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tools import JToolkit, jdown
from henrique.main.concepts.markettrend.trend_concept import MarkettrendTable, MarkettrendCollection, \
    MarkettrendDocument
from henrique.main.concepts.port.port_concept import PortCollection, PortTable
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.postgres.postgres_hub import PostgresHub


class Markettrend2MongoDB:

    @classmethod
    def postgres2j_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.postgres2j_iter, logging.DEBUG)

        with PostgresHub.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(MarkettrendTable.NAME))
            cursor.execute(sql)
            for t_list_chunk in ChunkToolkit.chunk_size2chunks(PostgresTool.fetch_iter(cursor), 100000):

                # logger.debug({"j":j})

                PortTable.name_en_list2port_id_list()

                def tuple2j_doc(t,i):
                    j_postgres = t[MarkettrendTable.index_json()]
                    j_doc = {MarkettrendDocument.F.SERVER: jdown(j_postgres, ["server","name"]),
                             MarkettrendDocument.F.CREATED_AT: datetime.fromisoformat(j_postgres["created_at"]),
                             MarkettrendDocument.F.SENDER_NAME: j_postgres["sender_name"],
                             MarkettrendDocument.F.PORT_ID: port_id,
                             MarkettrendDocument.F.TRADEGOOD_ID: tradegood_id,
                             MarkettrendDocument.F.RATE: rate,
                             MarkettrendDocument.F.TREND: trend,
                             }

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


        for i, j_list_chunk in enumerate(ChunkToolkit.chunk_size2chunks(j_list, chunk_size)):
            logger.debug({"i/n": "{}/{}".format(i*chunk_size, n)})
            j_pair_list = [(JToolkit.j_jpaths2filtered(j, [[MarkettrendDocument.F.KEY]]),j) for j in j_list_chunk]
            MongoDBToolkit.j_pair_iter2upsert(collection, j_pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers()
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    j_list = list(Markettrend2MongoDB.postgres2j_iter())
    logger.debug({"# j_list":len(j_list)})

    Markettrend2MongoDB.j_iter2mongodb(j_list)

if __name__ == "__main__":
    main()