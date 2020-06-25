import os
import sys
from datetime import datetime, timedelta

import pytz
import yaml

from foxylib.tools.datetime.timezone.timezone_tool import TimezoneTool
from foxylib.tools.native.native_tool import is_not_none
from future.utils import lmap, lfilter

from foxylib.tools.arithmetic.arithmetic_tool import ArithmeticTool
from foxylib.tools.collections.collections_tool import zip_strict

from foxylib.tools.datetime.datetime_tool import TimedeltaTool, DatetimeTool
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.json.yaml_tool import YAMLTool
from foxylib.tools.version.version_tool import VersionTool
from henrique.main.document.server.mongodb.server_doc import ServerDoc
from henrique.main.document.server.server import Server
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.tool.entity.datetime.timedelta.timedelta_entity import TimedeltaEntityUnit

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
    @VersionTool.inactive
    def str_timedelta2relativetimedelta(cls, str_timedelta, lang):
        suffix_format = JsonTool.down(cls.yaml(), [cls.Key.SUFFIX, lang])
        return suffix_format.format(str_timedelta)

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
    def datetime2text(cls, dt, tzdb):
        tz_abbr = TimezoneTool.tzdb2abbreviation(tzdb)

        dt_tz = DatetimeTool.astimezone(dt, pytz.timezone(tzdb))
        str_datetime = dt_tz.strftime("%I:%M:%S %p").lstrip("0")
        str_out = "{} ({})".format(str_datetime, tz_abbr)
        return str_out

    @classmethod
    def timedelta_lang2text(cls, td, lang):
        if td is None:
            return NanbanTimedeltaSuffix.lang2str_idk(lang)

        unit_td_list = [TimedeltaTool.unit_day(),
                     TimedeltaTool.unit_hour(),
                     TimedeltaTool.unit_minute(),
                     ]
        quotient_list = TimedeltaTool.timedelta_units2quotients(td, unit_td_list)

        def index2str(index):
            unit_td, quotient = unit_td_list[index], quotient_list[index]
            if not quotient:
                return None

            unit = TimedeltaEntityUnit.timedelta2unit(unit_td)
            str_unit = TimedeltaEntityUnit.v_unit_lang2str(quotient, unit, lang)
            return str_unit

        n = len(unit_td_list)
        word_list = lfilter(is_not_none, map(index2str, range(n)))

        str_out = " ".join(word_list)
        return str_out

    @classmethod
    def server2datetime_nanban(cls, server_codename, dt_pivot,):
        server_doc = ServerDoc.codename2doc(server_codename)
        if not server_doc:
            return None

        dt_nanban_raw = ServerDoc.doc2datetime_nanban(server_doc) if server_doc else None
        # utc_now = datetime.now(tz=pytz.utc)

        dt_nanban = DatetimeTool.from_pivot_period2next(dt_nanban_raw, dt_pivot, NanbanTimedelta.period())

        if dt_nanban != dt_nanban_raw:
            doc = {ServerDoc.Field.CODENAME: server_codename,
                   ServerDoc.Field.DATETIME_NANBAN: dt_nanban,
                   }
            ServerDoc.docs2upsert([doc])

        return dt_nanban






WARMER.warmup()
