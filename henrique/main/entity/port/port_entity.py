import logging
import os
import sys

import re
from functools import lru_cache
from future.utils import lmap
from nose.tools import assert_equal
from psycopg2.sql import SQL, Identifier

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, iter2duplicate_list, \
    iter2singleton, IterTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.regex.regex_tool import RegexTool, MatchTool
from foxylib.tools.string.string_tool import str2lower
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres
from henrique.main.tool.entity_tool import EntityTool

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
    def j_port_lang2name_list(cls, j_port, lang):
        logger = HenriqueLogger.func_level2logger(cls.j_port_lang2name, logging.DEBUG)
        name_list = jdown(j_port, [cls.F.NAMES, lang])
        return name_list

    @classmethod
    def j_port_lang2name(cls, j_port, lang):
        name_list = cls.j_port_lang2name(j_port, lang)
        return IterTool.first(name_list)

    @classmethod
    def j_port2name_en(cls, j_port):
        return cls.j_port_lang2name(j_port, "en")


    @classmethod
    def j_port2key(cls, j_port): return j_port[cls.F.KEY]

    @classmethod
    def jpath_names(cls): return [cls.F.NAMES]

    @classmethod
    def jpath_names_en(cls): return [cls.F.NAMES, "en"]

    @classmethod
    def jpath_names_ko(cls): return [cls.F.NAMES, "ko"]

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    @IterTool.wrap_iterable2list
    def j_port_list_all(cls):
        collection = PortCollection.collection()
        yield from MongoDBTool.result2j_doc_iter(collection.find({}))

    @classmethod
    def name_en_list2j_port_list(cls, name_en_list):
        norm = str2lower

        h = merge_dicts([{norm(cls.j_port2name_en(j_port)): j_port}
                         for j_port in cls.j_port_list_all()],
                        vwrite=vwrite_no_duplicate_key)

        j_port_list = [h.get(norm(x)) for x in name_en_list]
        return j_port_list


class PortEntity:
    TYPE = "port"

    @classmethod
    def query2norm(cls, q): return str2lower(q)

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _h_query2j_port(cls):
        logger = HenriqueLogger.func_level2logger(cls._h_query2j_port, logging.DEBUG)
        j_port_list = PortDoc.j_port_list_all()
        jpath = PortDoc.jpath_names()

        h_list = [{cls.query2norm(name): j_port}
                  for j_port in j_port_list
                  for name_list_lang in jdown(j_port, jpath).values()
                  for name in name_list_lang
                  ]

        logger.debug({"h_list":iter2duplicate_list(lmap(lambda h:iter2singleton(h.keys()), h_list)),
                      "jpath":jpath,
                      "j_doc_list[0]":j_port_list[0],
                      "query[0]":jdown(j_port_list[0],jpath)
                      })
        h = merge_dicts(h_list,vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def query2j_port(cls, query):
        str_norm = cls.query2norm(query)
        h = cls._h_query2j_port()
        return h.get(str_norm)


    @classmethod
    @WARMER.add(cond=not HenriqueEnv.skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def pattern(cls):
        h = cls._h_query2j_port()
        rstr = RegexTool.rstr_list2or(lmap(re.escape, h.keys()))
        return re.compile(rstr, re.I)

    @classmethod
    def _match2entity(cls, m):
        text = MatchTool.match2text(m)
        j_port = cls.query2j_port(text)

        j = {EntityTool.F.SPAN: MatchTool.match2span(m),
             EntityTool.F.TEXT: text,
             EntityTool.F.VALUE: j_port,
             }
        return j

    @classmethod
    def str2entity_list(cls, str_in):
        m_list = list(cls.pattern().finditer(str_in))

        entity_list = [cls._match2entity(m) for m in m_list]
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


