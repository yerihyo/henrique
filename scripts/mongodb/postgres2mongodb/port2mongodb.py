import logging
from functools import reduce

from psycopg2.sql import SQL, Identifier
from pymongo import WriteConcern

from foxylib.tools.collections.chunk_tool import ChunkTool
from foxylib.tools.collections.collections_tool import luniq, DictTool, lchain
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres
from henrique.main.entity.port.port_entity import PortTable, PortCollection, PortDoc


class Port2MongoDB:
    @classmethod
    def postgres2j_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.postgres2j_iter, logging.DEBUG)

        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT * from {}").format(Identifier(PortTable.NAME))
            cursor.execute(sql)
            for t in PostgresTool.fetch_iter(cursor):
                j = t[PortTable.index_json()]
                # logger.debug({"j":j})

                h_lang2names = {}
                for lang,name in j["name"].items():
                    h_lang2names[lang] = lchain(h_lang2names.get(lang, []), [name])

                for lang, nickname_list in j.get("nicknames",{}).items():
                    h_lang2names[lang] = lchain(h_lang2names.get(lang,[]), nickname_list)

                j[PortDoc.F.NAMES] = {lang:luniq(name_list) for lang, name_list in h_lang2names.items()}
                for k in ["name","nicknames"]:
                    j.pop(k,None)

                # logger.debug({'j["names"]':j["names"]})
                j[PortDoc.F.Key] = j["names"]["en"][0]

                yield j

    @classmethod
    def j_iter2mongodb(cls, j_iter, chunk_size = 100000):
        logger = HenriqueLogger.func_level2logger(cls.j_iter2mongodb, logging.DEBUG)
        j_list = list(j_iter)
        n = len(j_list)
        logger.debug({"n":n})


        write_concern = WriteConcern(w=3, wtimeout=chunk_size)
        collection = PortCollection.collection(write_concern=write_concern)


        for i, j_list_chunk in enumerate(ChunkTool.chunk_size2chunks(j_list, chunk_size)):
            logger.debug({"i/n": "{}/{}".format(i*chunk_size, n)})
            j_pair_list = [(JsonTool.j_jpaths2filtered(j, [[PortDoc.F.KEY]]),j) for j in j_list_chunk]
            MongoDBTool.j_pair_iter2upsert(collection, j_pair_list)


def main():
    HenriqueLogger.attach_stderr2loggers()
    logger = HenriqueLogger.func_level2logger(main, logging.DEBUG)

    j_list = list(Port2MongoDB.postgres2j_iter())
    logger.debug({"# j_list":len(j_list)})

    Port2MongoDB.j_iter2mongodb(j_list)

if __name__ == "__main__":
    main()