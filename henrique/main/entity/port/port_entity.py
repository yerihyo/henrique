import logging
import os
import sys

import re
from foxylib.tools.locale.locale_tool import LocaleTool
from functools import lru_cache
from future.utils import lmap
from nose.tools import assert_equal
from psycopg2.sql import SQL, Identifier

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, iter2duplicate_list, \
    iter2singleton, IterTool, lchain
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.entity.entity_tool import Entity, EntityConfig
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.nlp.gazetteer.gazetteer_matcher import GazetteerMatcher
from foxylib.tools.regex.regex_tool import RegexTool, MatchTool
from foxylib.tools.string.string_tool import str2lower, StringTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.locale.henrique_locale import HenriqueLocale
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
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
    def doc2key(cls, doc): return doc[cls.Field.KEY]


    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    @IterTool.wrap_iterable2list
    def doc_list_all(cls):
        collection = PortCollection.collection()
        yield from MongoDBTool.result2j_doc_iter(collection.find({}))


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_key2doc(cls):
        h = merge_dicts([{cls.doc2key(doc): doc} for doc in cls.doc_list_all()],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def key2doc(cls, key):
        return cls._dict_key2doc().get(key)





class PortEntity:
    TYPE = "port"

    @classmethod
    def text2norm(cls, q): return str2lower(q)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    def _dict_lang2matcher(cls,):
        return {lang: cls.lang2matcher(lang) for lang in HenriqueLocale.langs()}

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueLocale.lang_count()))
    def lang2matcher(cls, lang):
        doc_list = PortDoc.doc_list_all()
        langs_recognizable = HenriqueLocale.lang2langs_recognizable(lang)

        h_value2texts = [{PortDoc.doc2key(doc): [text
                                                 for lang in langs_recognizable
                                                 for text in PortDoc.doc_lang2text_list(doc, lang)]
                          }
                         for doc in doc_list]

        config = {GazetteerMatcher.Config.Key.NORMALIZER: cls.text2norm}
        matcher = GazetteerMatcher(h_value2texts, config)
        return matcher

    @classmethod
    def text2entity_list(cls, text_in, config=None):
        locale = EntityConfig.config2locale(config) or HenriqueLocale.DEFAULT
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


