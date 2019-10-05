import logging

from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tools import ChunkToolkit
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tools import JToolkit
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.mongodb.port.port_collection import PortTable, PortCollection
from henrique.main.hub.postgres.postgres_hub import PostgresHub


class Port:
    @classmethod
    def postgres2j_iter(cls):
        with PostgresHub.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(PortTable.NAME))
            cursor.execute(sql)
            for t in PostgresTool.fetch_iter(cursor):
                yield t[PortTable.index_json()]

    @classmethod
    def j_iter2mongodb(cls, j_iter, chunk_size = 100):
        logger = HenriqueLogger.func_level2logger(cls.j_iter2mongodb, logging.DEBUG)
        j_list = list(j_iter)
        n = len(j_list)
        logger.debug({"n":n})


        write_concern = WriteConcern(w=3, wtimeout=chunk_size)
        collection = PortCollection.collection(write_concern=write_concern)


        for i, j_list_chunk in enumerate(ChunkToolkit.chunk_size2chunks(j_list, chunk_size)):
            logger.debug({"i/n": "{}/{}".format(i*chunk_size, n)})
            j_pair_list = [(JToolkit.j_jpaths2filtered(j, [["name", "en"]]),j) for j in j_list_chunk]
            MongoDBToolkit.j_pair_iter2upsert(collection, j_pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers()
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    j_iter = Port.postgres2j_iter()
    Port.j_iter2mongodb(j_iter)

if __name__ == "__main__":
    main()