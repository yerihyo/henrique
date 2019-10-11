import logging
import os
import re
import sys
from functools import lru_cache

from future.utils import lmap
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
from henrique.main.entity.entity import EntityTool
from henrique.main.hub.env.henrique_env import HenriqueEnv
from henrique.main.hub.logger.logger import HenriqueLogger
from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

class PortEntity:
    NAME = "port"

    @classmethod
    def _query2qterm(cls, name): return str2lower(name)

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def h_qterm2j_doc(cls):
        logger = HenriqueLogger.func_level2logger(cls.h_qterm2j_doc, logging.DEBUG)
        j_doc_list = list(PortDocument.j_doc_iter_all())
        jpath_list = [PortDocument.jpath_name_en(), PortDocument.jpath_name_ko()]

        h_list = [{cls._query2qterm(jdown(j_doc, jpath)): j_doc}
         for j_doc, jpath in product(j_doc_list, jpath_list)]

        logger.debug({"h_list":iter2duplicate_list(lmap(lambda h:iter2singleton(h.keys()), h_list)),
                      #"j_doc_list":j_doc_list,
                      })
        h = merge_dicts(h_list,vwrite=vwrite_no_duplicate_key)
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



class PortCollection:
    COLLECTION_NAME = "port"

    class YAML:
        NAME = "name"

    @classmethod
    @WARMER.add(cond=EnvToolkit.key2is_not_true(HenriqueEnv.K.SKIP_WARMUP))
    @FunctionToolkit.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "port_collection.yaml")
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


class PortDocument:
    class Field:
        NAME = "name"
        CULTURE = "culture"
        REGION = "region"

        @classmethod
        def j_port2culture_name(cls, j_port):
            return j_port[cls.CULTURE]

        @classmethod
        def j_port_lang2name(cls, j_doc, lang):
            return jdown(j_doc, [lang, cls.NAME])

        @classmethod
        def j_port2j_culture(cls, j_port):
            from henrique.main.entity.culture.culture_entity import CultureDocument

            culture_name = cls.j_port2culture_name(j_port)
            j_culture = CultureDocument.name2j_doc(culture_name)
            return j_culture
    F = Field

    @classmethod
    def jpath_name_en(cls): return [cls.F.NAME, "en"]

    @classmethod
    def jpath_name_ko(cls): return [cls.F.NAME, "ko"]

    @classmethod
    def j_doc_iter_all(cls):
        collection = PortCollection.collection()
        yield from MongoDBToolkit.find_result2j_doc_iter(collection.find({}))


class PortTable:
    NAME = "unchartedwatersonline_port"

    @classmethod
    def index_json(cls): return 2

WARMER.warmup()


