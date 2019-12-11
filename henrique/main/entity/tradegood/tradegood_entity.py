import logging
import os
import re
import sys
from functools import lru_cache

from future.utils import lmap, lfilter
from nose.tools import assert_equal
from psycopg2.sql import Identifier, SQL

from foxylib.tools.collections.collections_tools import vwrite_no_duplicate_key, merge_dicts, iter2duplicate_list, \
    iter2singleton
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.env.env_tools import EnvToolkit
from foxylib.tools.function.function_tools import FunctionToolkit
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tools import jdown
from foxylib.tools.json.yaml_tools import YAMLToolkit
from foxylib.tools.regex.regex_tools import RegexToolkit
from foxylib.tools.string.string_tools import str2lower
from henrique.main.hub.entity.entity import Entity
from henrique.main.hub.env.henrique_env import HenriqueEnv
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub
from henrique.main.hub.postgres.postgres_hub import PostgresHub

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class TradegoodEntity:
    NAME = "tradegood"

    @classmethod
    def _query2qterm(cls, name): return str2lower(name)

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_qterm2j_doc(cls):
        logger = HenriqueLogger.func_level2logger(cls.h_qterm2j_doc, logging.DEBUG)
        j_doc_list = list(TradegoodDocument.j_doc_iter_all())
        jpath = TradegoodDocument.jpath_names()

        h_list = [{cls._query2qterm(name): j_doc}
                  for j_doc in j_doc_list
                  for name_list_lang in jdown(j_doc, jpath).values()
                  for name in name_list_lang
                  ]

        logger.debug({"h_list":iter2duplicate_list(lmap(lambda h:iter2singleton(h.keys()), h_list)),
                      "jpath":jpath,
                      "j_doc_list[0]":j_doc_list[0],
                      "query[0]":jdown(j_doc_list[0],jpath)
                      })

        qterm_list_duplicate = iter2duplicate_list(map(lambda h:iter2singleton(h.keys()),h_list))
        h_list_clean = lfilter(lambda h:iter2singleton(h.keys()) not in qterm_list_duplicate, h_list)

        h = merge_dicts(h_list_clean,vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def query2j_doc(cls, query):
        qterm = cls._query2qterm(query)
        h = cls.h_qterm2j_doc()
        return h.get(qterm)


    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern(cls):
        h = cls.h_qterm2j_doc()
        rstr = RegexToolkit.rstr_list2or(lmap(re.escape, h.keys()))
        return re.compile(rstr, re.I)


    @classmethod
    def str2entity_list(cls, str_in):
        m_list = list(cls.pattern().finditer(str_in))

        entity_list = [merge_dicts([Entity.Builder.match2h(m),
                                    Entity.Builder.type2h(cls.NAME),
                                    ])
                       for m in m_list]
        return entity_list



class TradegoodCollection:
    COLLECTION_NAME = "tradegood"

    class YAML:
        NAME = "name"

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "tradegood_collection.yaml")
        j = YAMLToolkit.filepath2j(filepath)
        return j

    @classmethod
    def lang2name(cls, lang):
        j_yaml = cls.j_yaml()
        return jdown(j_yaml, [cls.YAML.NAME,lang])

    @classmethod
    def collection(cls, *_, **__):
        db = MongoDBHub.db()
        return db.get_collection(cls.COLLECTION_NAME, *_, **__)


class TradegoodDocument:
    class Field:
        KEY = "key"
        NAMES = "names"
        CULTURE = "culture"
        REGION = "region"
    F = Field



    @classmethod
    def j_tradegood2culture_name(cls, j_tradegood):
        return j_tradegood[cls.F.CULTURE]

    @classmethod
    def j_tradegood_lang2name(cls, j_tradegood, lang):
        logger = HenriqueLogger.func_level2logger(cls.j_tradegood_lang2name, logging.DEBUG)
        name_list = jdown(j_tradegood, [cls.F.NAMES, lang])

        # logger.debug({"j_tradegood":j_tradegood,
        #               "lang":lang,
        #               "name_list":name_list,
        #               })
        return name_list[0]

    @classmethod
    def j_tradegood2name_en(cls, j_tradegood):
        return cls.j_tradegood_lang2name(j_tradegood, "en")


    @classmethod
    def jpath_names(cls): return [cls.F.NAMES]

    @classmethod
    def jpath_names_en(cls): return [cls.F.NAMES, "en"]

    @classmethod
    def jpath_names_ko(cls): return [cls.F.NAMES, "ko"]

    @classmethod
    def j_doc_iter_all(cls):
        collection = TradegoodCollection.collection()
        yield from MongoDBToolkit.result2j_doc_iter(collection.find({}))

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _h_doc_id2j_doc(cls):
        return MongoDBToolkit.j_doc_iter2h_doc_id2j_doc(cls.j_doc_iter_all())

    @classmethod
    def tradegood_id2j_doc(cls, tradegood_id):
        h = cls._h_doc_id2j_doc()
        return h.get(tradegood_id)

    @classmethod
    def name_en_list2doc_id_list(cls, name_en_list):
        norm = str2lower

        h = merge_dicts([{norm(cls.j_tradegood2name_en(j_port)): MongoDBToolkit.j_doc2id(j_port)}
                         for j_port in cls.j_doc_iter_all()],
                        vwrite=vwrite_no_duplicate_key)

        doc_id_list = [h[norm(x)] for x in name_en_list]
        return doc_id_list

class TradegoodTable:
    NAME = "unchartedwatersonline_tradegood"

    @classmethod
    def index_json(cls): return 2

    @classmethod
    def name_en_list2tradegood_id_list(cls, name_en_list):
        h = {}
        with PostgresHub.cursor() as cursor:
            sql = SQL("SELECT id, name_en from {}").format(Identifier(cls.NAME))
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                assert_equal(len(t), 2)
                h[str2lower(t[1])] = t[0]

        tradegood_id_list = [h.get(str2lower(name_en)) for name_en in name_en_list]
        return tradegood_id_list

WARMER.warmup()


