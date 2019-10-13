import logging
import os
import re
import sys
from functools import lru_cache

from future.utils import lmap, lfilter
from itertools import product

from foxylib.tools.collections.collections_tools import vwrite_no_duplicate_key, merge_dicts, lchain, \
    iter2duplicate_list, iter2singleton
from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.env.env_tools import EnvToolkit
from foxylib.tools.function.function_tools import FunctionToolkit
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tools import jdown
from foxylib.tools.json.yaml_tools import YAMLToolkit
from foxylib.tools.regex.regex_tools import RegexToolkit
from foxylib.tools.string.string_tools import str2lower
from henrique.main.hub.entity.entity_tool import EntityTool
from henrique.main.hub.env.henrique_env import HenriqueEnv
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class MarketpriceEntity:
    NAME = "tradegood"

    @classmethod
    def _query2qterm(cls, name): return str2lower(name)

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_qterm2j_doc(cls):
        logger = HenriqueLogger.func_level2logger(cls.h_qterm2j_doc, logging.DEBUG)
        j_doc_list = list(MarketpriceDocument.j_doc_iter_all())
        jpath = MarketpriceDocument.jpath_names()

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

        entity_list = [merge_dicts([EntityTool.F.match2h(m),
                                    EntityTool.F.type2h(cls.NAME),
                                    ])
                       for m in m_list]
        return entity_list



class MarkettrendCollection:
    COLLECTION_NAME = "markettrend"

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


class MarketpriceDocument:
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
        logger = HenriqueLogger.func_level2logger(cls.j_tradegood2culture_name, logging.DEBUG)
        name_list = jdown(j_tradegood, [cls.F.NAMES, lang])

        logger.debug({"j_tradegood":j_tradegood,
                      "lang":lang,
                      "name_list":name_list,
                      })
        return name_list[0]

        # @classmethod
        # def j_tradegood2j_culture(cls, j_tradegood):
        #     from henrique.main.action.culture.culture_entity import CultureDocument
        #
        #     culture_name = cls.j_tradegood2culture_name(j_tradegood)
        #     j_culture = CultureDocument.name2j_doc(culture_name)
        #     return j_culture


    @classmethod
    def jpath_names(cls): return [cls.F.NAMES]

    @classmethod
    def jpath_names_en(cls): return [cls.F.NAMES, "en"]

    @classmethod
    def jpath_names_ko(cls): return [cls.F.NAMES, "ko"]

    @classmethod
    def j_doc_iter_all(cls):
        collection = MarkettrendCollection.collection()
        yield from MongoDBToolkit.find_result2j_doc_iter(collection.find({}))


class MarketpriceTable:
    NAME = "unchartedwatersonline_tradegood"

    @classmethod
    def index_json(cls): return 2

WARMER.warmup()


