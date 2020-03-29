from functools import lru_cache

from foxylib.tools.collections.collections_tool import IterTool, merge_dicts, vwrite_no_duplicate_key, DictTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.entity.port.port_entity import Port
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb


class PortCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("port", *_, **__)



class PortDoc:
    class Field:
        KEY = "key"
        NAMES = "names"
        CULTURE = "culture"
        REGION = "region"
    F = Field

    @classmethod
    def doc2dict_lang2aliases(cls, doc):
        return doc.get(cls.Field.NAMES) or {}

    @classmethod
    def doc_lang2text_list(cls, doc, lang):
        h_lang2aliases = cls.doc2dict_lang2aliases(doc)
        return h_lang2aliases.get(lang) or []

    @classmethod
    def doc_lang2name(cls, doc, lang):
        return IterTool.first(cls.doc_lang2text_list(doc, lang))

    @classmethod
    def doc2key(cls, doc): return doc[cls.Field.KEY]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def doc_list_all(cls):
        collection = PortCollection.collection()
        doc_iter = MongoDBTool.result2j_doc_iter(collection.find({}))
        return list(doc_iter)

    @classmethod
    def dict_codename2port_partial(cls):
        doc_list = cls.doc_list_all()

        def doc2port_partial(doc):
            langs = ["en", "ko"]

            tradegoods = doc.get("tradegoods") or []
            port_partial = {Port.Field.ALIASES: {lang: cls.doc_lang2text_list(doc, lang) for lang in langs},
                            Port.Field.PRODUCTS: [JsonTool.down(tg, ["name", "en"]) for tg in tradegoods]
                            }
            return port_partial

        return merge_dicts([{PortDoc.doc2key(doc): doc2port_partial(doc)}
                            for doc in doc_list],
                           vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                           )



    # @classmethod
    # def doc2products(cls, doc):
    #     return doc.get("tradegoods") or []


    @classmethod
    def tradegoods2docs_MONGO(cls, tg_codenames):
        tg_codename_list = list(tg_codenames)

        collection = PortCollection.collection()
        mongo_query = {"tradegoods.name.en": {"$in": tg_codename_list}}
        doc_iter = MongoDBTool.result2j_doc_iter(collection.find(mongo_query))
        yield from doc_iter
