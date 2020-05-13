import logging
import os
import sys

from functools import lru_cache
from future.utils import lmap

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, DictTool, lchain
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.document.tradegood.tradegood import Tradegood
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class TradegoodCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("tradegood", *_, **__)


class TradegoodDoc:
    class Field:
        KEY = "key"
        NAMES = "names"
    F = Field

    @classmethod
    def doc_lang2names(cls, doc, lang):
        names = JsonTool.down(doc, [cls.Field.NAMES, lang]) or []
        return names

    @classmethod
    def doc2key(cls, doc): return doc[cls.Field.KEY]

    @classmethod
    def doc_list_all(cls):
        collection = TradegoodCollection.collection()
        return lmap(MongoDBTool.bson2json, collection.find({}))

    @classmethod
    def dict_codename2tradegood_partial(cls):

        def doc2tradegood_partial(doc):
            langs = ["en", "ko"]

            port_partial = {Tradegood.Field.ALIASES: {lang: cls.doc_lang2names(doc, lang) for lang in langs},
                            Tradegood.Field.CODENAME: cls.doc2key(doc)
                            }
            return port_partial

        return merge_dicts([{cls.doc2key(doc): doc2tradegood_partial(doc)}
                            for doc in cls.doc_list_all()],
                           vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                           )

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2id(cls,):
        doc_list = cls.doc_list_all()

        h = merge_dicts([{cls.doc2key(doc): MongoDBTool.doc2id(doc)}
                         for doc in doc_list],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def codename2id(cls, codename):
        h = cls._dict_codename2id()
        return h[codename]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_id2codename(cls, ):
        doc_list = cls.doc_list_all()

        h = merge_dicts([{MongoDBTool.doc2id(doc): cls.doc2key(doc)}
                         for doc in doc_list],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def id2codename(cls, doc_id):
        logger = HenriqueLogger.func_level2logger(cls.id2codename, logging.DEBUG)
        h = cls._dict_id2codename()
        logger.debug({"h": h})
        return h[doc_id]

class Mongodb2Googlesheets:
    @classmethod
    def docs2sheet_name_en(cls, doc_list):
        def doc2sheet_name_en_row(doc):
            key = TradegoodDoc.doc2key(doc)
            name_list_en = TradegoodDoc.doc_lang2names(doc, "en")

            return lchain([key], name_list_en)

        for doc in doc_list:
            yield doc2sheet_name_en_row(doc)

    @classmethod
    def docs2sheet_name_ko(cls, doc_list):
        def doc2sheet_name_ko_row(doc):
            key = TradegoodDoc.doc2key(doc)
            name_list_en = TradegoodDoc.doc_lang2names(doc, "ko")

            return lchain([key], name_list_en)

        for doc in doc_list:
           yield doc2sheet_name_ko_row(doc)

    @classmethod
    def rows2text(cls, rows):
        return "\n".join(map(lambda row: ",".join(map(str, row)), rows))


    @classmethod
    def collection2sheets(cls,):
        doc_list = list(TradegoodCollection.collection().find())
        block_list = [cls.rows2text(cls.docs2sheet_name_en(doc_list)),
                      cls.rows2text(cls.docs2sheet_name_ko(doc_list)),
                      ]
        print("\n\n".join(block_list))


def main():
    Mongodb2Googlesheets.collection2sheets()

if __name__ == '__main__':
    main()
