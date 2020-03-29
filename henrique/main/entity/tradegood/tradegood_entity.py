import os
import sys

from functools import lru_cache
from nose.tools import assert_equal
from psycopg2.sql import Identifier, SQL

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
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
    @IterTool.f_iter2f_list
    def doc_list_all(cls):
        collection = TradegoodCollection.collection()
        yield from MongoDBTool.result2j_doc_iter(collection.find({}))


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



class TradegoodEntity:
    TYPE = "tradegood"

    @classmethod
    def text2norm(cls, text): return str2lower(text)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    def _dict_lang2matcher(cls,):
        return {lang: cls.lang2matcher(lang) for lang in HenriqueLocale.langs()}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        doc_list = TradegoodDoc.doc_list_all()
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        def doc2texts(doc):
            for _lang in langs_recognizable:
                yield from TradegoodDoc.doc_lang2text_list(doc, _lang)

        h_value2texts = merge_dicts([{TradegoodDoc.doc2codename(doc): list(doc2texts(doc))} for doc in doc_list],
                                    vwrite=vwrite_no_duplicate_key)

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm}
        matcher = GazetteerMatcher(h_value2texts, config)
        return matcher

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueEntity.Cache.DEFAULT_SIZE))
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


#
#
#
# class TradegoodEntity:
#     TYPE = "tradegood"
#
#     @classmethod
#     def _query2qterm(cls, name): return str2lower(name)
#
#     @classmethod
#     @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def h_qterm2j_doc(cls):
#         logger = HenriqueLogger.func_level2logger(cls.h_qterm2j_doc, logging.DEBUG)
#         j_doc_list = list(TradegoodDoc.j_doc_iter_all())
#         jpath = TradegoodDoc.jpath_names()
#
#         h_list = [{cls._query2qterm(name): j_doc}
#                   for j_doc in j_doc_list
#                   for name_list_lang in jdown(j_doc, jpath).values()
#                   for name in name_list_lang
#                   ]
#
#         logger.debug({"h_list":iter2duplicate_list(lmap(lambda h:iter2singleton(h.keys()), h_list)),
#                       "jpath":jpath,
#                       "j_doc_list[0]":j_doc_list[0],
#                       "query[0]":jdown(j_doc_list[0],jpath)
#                       })
#
#         qterm_list_duplicate = iter2duplicate_list(map(lambda h:iter2singleton(h.keys()),h_list))
#         h_list_clean = lfilter(lambda h:iter2singleton(h.keys()) not in qterm_list_duplicate, h_list)
#
#         h = merge_dicts(h_list_clean,vwrite=vwrite_no_duplicate_key)
#         return h
#
#     @classmethod
#     def query2j_doc(cls, query):
#         qterm = cls._query2qterm(query)
#         h = cls.h_qterm2j_doc()
#         return h.get(qterm)
#
#
#     @classmethod
#     @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def pattern(cls):
#         h = cls.h_qterm2j_doc()
#         rstr = RegexTool.rstr_list2or(lmap(re.escape, h.keys()))
#         return re.compile(rstr, re.I)
#
#
#     @classmethod
#     def text2entity_list(cls, text_in):
#         m_list = list(cls.pattern().finditer(text_in))
#
#         def match2entity(m):
#             span = m.span()
#             text = StringTool.str_span2substr(text_in, span)
#             entity = {Entity.Field.TYPE: cls.TYPE,
#                       Entity.Field.SPAN: span,
#                       Entity.Field.TEXT: text,
#                       Entity.Field.VALUE: text,
#                       }
#             return entity
#         entity_list = lmap(match2entity, m_list)
#         return entity_list

class TradegoodTable:
    NAME = "unchartedwatersonline_tradegood"

    @classmethod
    def index_json(cls): return 2

    @classmethod
    def name_en_list2tradegood_id_list(cls, name_en_list):
        h = {}
        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT id, name_en from {}").format(Identifier(cls.NAME))
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                assert_equal(len(t), 2)
                h[str2lower(t[1])] = t[0]

        tradegood_id_list = [h.get(str2lower(name_en)) for name_en in name_en_list]
        return tradegood_id_list

WARMER.warmup()


