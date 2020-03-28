import os
import sys

from functools import lru_cache
from future.utils import lfilter, lmap
from nose.tools import assert_equal
from psycopg2.sql import SQL, Identifier

from foxylib.tools.cache.cache_tool import CacheTool
from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.locale.locale_tool import LocaleTool
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.entity.henrique_entity import Entity, HenriqueEntity
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


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
    def doc2dict_lang2texts(cls, doc):
        return doc.get(cls.Field.NAMES) or {}

    @classmethod
    def doc_lang2text_list(cls, doc, lang):
        h_lang2texts = cls.doc2dict_lang2texts(doc)
        return h_lang2texts.get(lang) or []

    @classmethod
    def doc_lang2name(cls, doc, lang):
        return IterTool.first(cls.doc_lang2text_list(doc, lang))

    @classmethod
    def doc2codename(cls, doc): return doc[cls.Field.KEY]

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def doc_list_all(cls):
        collection = PortCollection.collection()
        doc_iter = MongoDBTool.result2j_doc_iter(collection.find({}))
        return list(doc_iter)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2doc(cls):
        h = merge_dicts([{cls.doc2codename(doc): doc} for doc in cls.doc_list_all()],
                        vwrite=vwrite_no_duplicate_key)
        # raise Exception(h)
        return h

    @classmethod
    def codename2doc(cls, codename):
        return cls._dict_codename2doc().get(codename)

    @classmethod
    def doc2products(cls, doc):
        return doc.get("tradegoods") or []

    @classmethod
    def port_tradegood2is_sold(cls, port, tg_codename):
        products = cls.doc2products(port)

        for product in products:
            tg_codename_product = Product.product2tradegood_codename(product)
            if tg_codename == tg_codename_product:
                return True
        return False

    @classmethod
    def tradegood2docs(cls, tg_codename):
        return lfilter(lambda port: cls.port_tradegood2is_sold(port, tg_codename), cls.doc_list_all())

    @classmethod
    def tradegoods2docs_MONGO(cls, tg_codenames):
        tg_codename_list = list(tg_codenames)

        collection = PortCollection.collection()
        mongo_query = {"tradegoods.name.en": {"$in": tg_codename_list}}
        doc_iter = MongoDBTool.result2j_doc_iter(collection.find(mongo_query))
        yield from doc_iter


class Product:
    @classmethod
    def product2tradegood_codename(cls, product):
        return JsonTool.down(product, ["name", "en"])





class PortEntity:
    TYPE = "port"

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    def _dict_lang2matcher(cls,):
        return {lang: cls.lang2matcher(lang) for lang in HenriqueLocale.langs()}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        doc_list = PortDoc.doc_list_all()
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        def doc2texts(doc):
            for _lang in langs_recognizable:
                yield from PortDoc.doc_lang2text_list(doc, _lang)

        h_value2texts = merge_dicts([{PortDoc.doc2codename(doc): list(doc2texts(doc))} for doc in doc_list],
                                    vwrite=vwrite_no_duplicate_key)

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm}
        matcher = GazetteerMatcher(h_value2texts, config)
        return matcher

    @classmethod
    @CacheTool.cache2hashable(cache=lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE),
                              f_pair=CacheTool.JSON.func_pair(), )
    def text2entity_list(cls, text_in, config=None):
        locale = Entity.Config.config2locale(config) or HenriqueLocale.DEFAULT
        lang = LocaleTool.locale2lang(locale) or LocaleTool.locale2lang(HenriqueLocale.DEFAULT)

        matcher = cls.lang2matcher(lang)
        span_value_list = matcher.text2span_value_list(text_in)

        entity_list = [{Entity.Field.SPAN: span,
                        Entity.Field.TEXT: StringTool.str_span2substr(text_in, span),
                        Entity.Field.VALUE: value,
                        Entity.Field.TYPE: cls.TYPE,
                        }
                       for span, value in span_value_list]

        return entity_list







class PortTable:
    NAME = "unchartedwatersonline_port"

    @classmethod
    def index_json(cls): return 2

    @classmethod
    def name_en_list2port_id_list(cls, name_en_list):
        h = {}
        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT id, name_en FROM {}").format(Identifier(cls.NAME), )
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                assert_equal(len(t), 2)
                h[str2lower(t[1])] = t[0]


        port_id_list = [h.get(str2lower(name_en)) for name_en in name_en_list]
        return port_id_list


WARMER.warmup()


