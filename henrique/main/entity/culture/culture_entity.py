import os
import sys
from functools import lru_cache

from foxylib.tools.env.env_tool import EnvTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import jdown
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.singleton.cache.henrique_cache import HenriqueCache
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class CultureCollection:
    COLLECTION_NAME = "culture"

    class YAML:
        NAME = "name"

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def j_yaml(cls):
        filepath = os.path.join(FILE_DIR, "culture_collection.yaml")
        j = YAMLTool.filepath2j(filepath)
        return j

    @classmethod
    def lang2name(cls, lang):
        j_yaml = cls.j_yaml()
        return jdown(j_yaml, [cls.YAML.NAME,lang])

    @classmethod
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection(cls.COLLECTION_NAME, *_, **__)

class CultureDocument:
    class Field:
        NAME = "name"

        def j_culture_lang2name(cls, j_culture, lang):
            return jdown(j_culture, [lang, cls.NAME])
    F = Field

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=HenriqueCache.DEFAULT_SIZE))
    def name2j_doc(cls, name):
        pass


