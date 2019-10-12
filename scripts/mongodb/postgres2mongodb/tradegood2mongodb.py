import logging

from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tools import ChunkToolkit
from foxylib.tools.collections.collections_tools import luniq, lchain
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tools import JToolkit
from henrique.main.entity.tradegood.tradegood_entity import TradegoodTable, TradegoodCollection, TradegoodDocument
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.postgres.postgres_hub import PostgresHub


class Tradegood2MongoDB:
    @classmethod
    def postgres2j_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.postgres2j_iter, logging.DEBUG)

        with PostgresHub.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(TradegoodTable.NAME))
            cursor.execute(sql)
            for t in PostgresTool.fetch_iter(cursor):
                j = t[TradegoodTable.index_json()]
                # logger.debug({"j":j})

                h_lang2names = {}
                for lang,name in j["name"].items():
                    h_lang2names[lang] = lchain(h_lang2names.get(lang, []), [name])

                for lang, nickname_list in j.get("nicknames",{}).items():
                    h_lang2names[lang] = lchain(h_lang2names.get(lang,[]), nickname_list)

                j[TradegoodDocument.F.NAMES] = {lang:luniq(name_list) for lang, name_list in h_lang2names.items()}
                for k in ["name","nicknames"]:
                    j.pop(k,None)

                # logger.debug({'j["names"]':j["names"]})
                j[TradegoodDocument.F.KEY] = j["names"]["en"][0]

                yield j

    @classmethod
    def j_iter2mongodb(cls, j_iter, chunk_size = 100000):
        logger = HenriqueLogger.func_level2logger(cls.j_iter2mongodb, logging.DEBUG)
        j_list = list(j_iter)
        n = len(j_list)
        logger.debug({"n":n})


        write_concern = WriteConcern(w=3, wtimeout=chunk_size)
        collection = TradegoodCollection.collection(write_concern=write_concern)


        for i, j_list_chunk in enumerate(ChunkToolkit.chunk_size2chunks(j_list, chunk_size)):
            logger.debug({"i/n": "{}/{}".format(i*chunk_size, n)})
            j_pair_list = [(JToolkit.j_jpaths2filtered(j, [[TradegoodDocument.F.KEY]]),j) for j in j_list_chunk]
            MongoDBToolkit.j_pair_iter2upsert(collection, j_pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers()
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    j_list = list(Tradegood2MongoDB.postgres2j_iter())
    logger.debug({"# j_list":len(j_list)})

    Tradegood2MongoDB.j_iter2mongodb(j_list)

if __name__ == "__main__":
    main()