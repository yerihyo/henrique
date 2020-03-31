import os
import sys

from functools import lru_cache

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, DictTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.entity.tradegood.tradegood import Tradegood
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
    def doc_iter_all(cls):
        collection = TradegoodCollection.collection()
        yield from MongoDBTool.result2j_doc_iter(collection.find({}))

    @classmethod
    def dict_codename2tradegood_partial(cls):

        def doc2tradegood_partial(doc):
            langs = ["en", "ko"]

            port_partial = {Tradegood.Field.ALIASES: {lang: cls.doc_lang2names(doc, lang) for lang in langs},
                            Tradegood.Field.CODENAME: cls.doc2key(doc)
                            }
            return port_partial

        return merge_dicts([{cls.doc2key(doc): doc2tradegood_partial(doc)}
                            for doc in cls.doc_iter_all()],
                           vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                           )
