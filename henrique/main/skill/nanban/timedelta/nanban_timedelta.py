import os
import sys
from datetime import datetime, timedelta

import pytz
import yaml

from foxylib.tools.arithmetic.arithmetic_tool import ArithmeticTool
from foxylib.tools.collections.collections_tool import zip_strict

from foxylib.tools.date.date_tools import TimedeltaTool
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from henrique.main.document.server.mongodb.server_doc import ServerDoc
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.tool.entity.time.timedelta.timedelta_entity import TimedeltaUnit

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class NanbanTimedeltaSuffix:
    class Key:
        SUFFIX = "suffix"
        I_DONT_KNOW = "i_dont_know"

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def yaml(cls):
        filepath = os.path.join(FILE_DIR, "suffix.yaml")
        j_yaml = YAMLTool.filepath2j(filepath, yaml.SafeLoader)
        return j_yaml

    @classmethod
    def str_lang2suffixed(cls, str_in, lang):
        suffix_format = JsonTool.down(cls.yaml(), [cls.Key.SUFFIX, lang])
        return suffix_format.format(str_in)

    @classmethod
    def lang2str_idk(cls, lang):
        return JsonTool.down(cls.yaml(), [cls.Key.I_DONT_KNOW, lang])


class NanbanTimedelta:


    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def period(cls):
        seconds = 2 * 60 * 60 + 1 * 60
        return timedelta(seconds=seconds)


    @classmethod
    def timedelta_lang2text(cls, td, lang):
        unit_list = [TimedeltaTool.unit_day(),
                     TimedeltaTool.unit_hour(),
                     TimedeltaTool.unit_minute(),
                     ]
        quotient_list = TimedeltaTool.timedelta_units2quotients(td, unit_list)

        str_timedelta = " ".join([TimedeltaUnit.v_unit_lang2str(v, unit, lang)
                                  for v, unit in zip_strict(quotient_list, unit_list) if v])

        return NanbanTimedeltaSuffix.str_lang2suffixed(str_timedelta, lang)


    @classmethod
    def server_lang2str(cls, server, lang):
        server_doc = ServerDoc.codename2doc(Server.server2codename(server))
        if not server_doc:
            return NanbanTimedeltaSuffix.lang2str_idk(lang)

        nanban_time_raw = ServerDoc.doc2nanban_time(server_doc) if server_doc else None
        utc_now = datetime.now(tz=pytz.utc)

        q = ArithmeticTool.divide_and_ceil(utc_now - nanban_time_raw, cls.period())

        nanban_time = nanban_time_raw + q * cls.period()

        if q:
            doc = {ServerDoc.Field.CODENAME: Server.server2codename(server),
                   ServerDoc.Field.NANBAN_TIME: nanban_time,
                   }
            ServerDoc.update([doc])

        td = nanban_time - utc_now

        return cls.timedelta_lang2text(td, lang)




WARMER.warmup()
