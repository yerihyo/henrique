from functools import lru_cache
from future.utils import lmap
from nose.tools import assert_not_in

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, lchain
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from henrique.main.document.port.port import Product
from henrique.main.document.port.port_entity import Port
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
        doc_iter = map(MongoDBTool.bson2json,collection.find({}))
        return list(doc_iter)

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

        h = merge_dicts([{MongoDBTool.doc2id(doc):cls.doc2key(doc)}
                         for doc in doc_list],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def id2codename(cls, doc_id):
        h = cls._dict_id2codename()
        return h[doc_id]

    @classmethod
    def doc2product_list(cls, doc):
        tradegoods = doc.get("tradegoods") or []
        product_list = [{Product.Field.TRADEGOOD: JsonTool.down(tg, ["name", "en"]),
                         Product.Field.PRICE: JsonTool.down(tg, ["price"]),
                         }
                        for tg in tradegoods]
        return product_list

    @classmethod
    def dict_codename2port(cls):
        doc_list = cls.doc_list_all()

        def doc2port_partial(doc):
            langs = ["en", "ko"]

            product_list = cls.doc2product_list(doc)

            port_partial = {Port.Field.ALIASES: {lang: cls.doc_lang2text_list(doc, lang) for lang in langs},
                            Port.Field.PRODUCTS: product_list,
                            Port.Field.CODENAME: PortDoc.doc2key(doc)
                            }
            return port_partial

        return merge_dicts([{PortDoc.doc2key(doc): doc2port_partial(doc)}
                            for doc in doc_list],
                           vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                           )



    # @classmethod
    # def doc2products(cls, doc):
    #     return doc.get("tradegoods") or []


    # @classmethod
    # def tradegoods2docs_MONGO(cls, tg_codenames):
    #     tg_codename_list = list(tg_codenames)
    #
    #     collection = PortCollection.collection()
    #     mongo_query = {"tradegoods.name.en": {"$in": tg_codename_list}}
    #     doc_iter = map(MongoDBTool.bson2json,collection.find(mongo_query))
    #     yield from doc_iter


class Mongodb2Googlesheets:
    @classmethod
    def docs2sheet_name_en(cls, doc_list):
        def doc2sheet_name_en_row(doc):
            key = PortDoc.doc2key(doc)
            name_list_en = PortDoc.doc_lang2text_list(doc, "en")

            return lchain([key], name_list_en)

        for doc in doc_list:
            yield doc2sheet_name_en_row(doc)

    @classmethod
    def docs2sheet_name_ko(cls, doc_list):
        def doc2sheet_name_ko_row(doc):
            key = PortDoc.doc2key(doc)
            name_list_en = PortDoc.doc_lang2text_list(doc, "ko")

            return lchain([key], name_list_en)

        for doc in doc_list:
           yield doc2sheet_name_ko_row(doc)

    @classmethod
    def docs2sheet_product(cls, doc_list):
        def doc2sheet_product_rows(doc):
            codename = PortDoc.doc2key(doc)
            product_list = PortDoc.doc2product_list(doc)
            for product in product_list:
                tradegood_codename = Product.product2tradegood(product)
                price = Product.product2price(product)

                row = [codename, tradegood_codename]
                if price:
                    row.append(price)

                assert_not_in(None, row)
                yield row

        for doc in doc_list:
            yield from doc2sheet_product_rows(doc)

    @classmethod
    def rows2text(cls, rows):
        return "\n".join(map(lambda row: ",".join(map(str, row)), rows))


    @classmethod
    def collection2sheets(cls,):
        doc_list = list(PortCollection.collection().find())
        block_list = [cls.rows2text(cls.docs2sheet_name_en(doc_list)),
                      cls.rows2text(cls.docs2sheet_name_ko(doc_list)),
                      cls.rows2text(cls.docs2sheet_product(doc_list)),
                      ]
        print("\n\n".join(block_list))



def main():
    Mongodb2Googlesheets.collection2sheets()

if __name__ == '__main__':
    main()
