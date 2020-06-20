import logging
import os
import sys

from datetime import time, timedelta

from foxylib.tools.datetime.datetime_tool import TimeTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from functools import lru_cache
from future.utils import lmap, lfilter
from nose.tools import assert_equal

from foxylib.tools.span.span_tool import SpanTool
from foxylib.tools.string.string_tool import str2lower
from foxylib.tools.entity.entity_tool import FoxylibEntity

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class AMPM:
    AM = "AM"
    PM = "PM"

    @classmethod
    def hour2is_ampm_certain(cls, hour):
        if hour >= 13:
            return True

        if hour in {0, 24}:
            return True

        return False

    @classmethod
    def hour2ampm(cls, hour):

        if hour >= 12:
            return cls.PM

        if 0 <= hour < 12:
            return cls.AM

        if hour in {0, 24}:
            return cls.AM

        raise NotImplementedError({"hour": hour})

    @classmethod
    def time_ampm2adjusted(cls, time_in, ampm):
        if ampm == cls.PM:
            if time_in.hour >= 12:
                return time_in
            return time(time_in.hour + 12, time_in.minute, time_in.second)

        if ampm == cls.AM and time_in.hour == 12:
            return time(0, time_in.minute, time_in.second)

        return time_in


class TimeEntity:
    @classmethod
    def str2norm(cls, s_in):
        s_out = str2lower(s_in)

        assert_equal(len(s_in), len(s_out))
        return s_out

    @classmethod
    def value2has_ampm(cls, value):
        return value[1] is not None

    @classmethod
    def value_timedelta2adjusted(cls, value_in, td):
        time_in = TimeEntity.value2time(value_in)
        time_out = TimeTool.time_timedelta2adjusted(time_in, td)

        value_out = TimeEntity.time2value(time_out, ampm=cls.value2has_ampm(value_in))
        return value_out


    @classmethod
    def time2value(cls, time_in, ampm=None, ):
        hour = time_in.hour

        def ampm2updated():
            ampm_hour = AMPM.hour2ampm(hour)

            if AMPM.hour2is_ampm_certain(hour):
                return ampm_hour

            if ampm is True:
                return ampm_hour

            if ampm:
                return ampm

            return None

        _ampm = ampm2updated()

        time_revised = TimeTool.time_timedelta2adjusted(time_in, -timedelta(hours=12)) if hour >= 13 else time_in
        rv = (time_revised.strftime("%I:%M:%S"), _ampm)
        return rv

    @classmethod
    def value2time(cls, value):
        str_hms, ampm = value
        h, m, s = str_hms.split(':')

        time_raw = time(int(h), int(m), int(s))
        return AMPM.time_ampm2adjusted(time_raw, ampm)

    @classmethod
    # @PerformanceTool.profile_duration
    def text2entity_list(cls, s, config=None,):

        step = EntityTool.Config.config2step(config) or EntityTool.Step.Value.PRECISION

        if step == EntityTool.Step.Value.PRECISION:
            return cls._str2entity_list_precision(s, config)

        if step == EntityTool.Step.Value.RECALL:
            is_focused = EntityTool.Config.entity_type2is_focused(TimeEntity.ENTITY_TYPE, config)
            return cls._str2entity_list_recall(s, is_focused)

    @classmethod
    def _str2entity_list_precision(cls, str_in, config=None):
        is_focused = EntityTool.Config.entity_type2is_focused(TimeEntity.ENTITY_TYPE, config)
        entity_list_recall = cls._str2entity_list_recall(str_in, is_focused)

        from linc_utils.entity_identification.entities.timedelta.time_frequency.time_frequency_entity import \
            TimeFrequencyEntity

        config_recall = merge_dicts([config, {EntityTool.Config.Key.STEP: EntityTool.Step.Value.RECALL}],
                                    vwrite=vwrite_overwrite)
        entity_list_priority = TimeFrequencyEntity.str2entity_list(str_in, config=config_recall)

        entity_list_uncovered = EntityTool.entity_list2uncovered(entity_list_recall, entity_list_priority, )

        return entity_list_uncovered

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=256))
    def _str2entity_list_recall(cls, s, is_focused):

        def entity_iter():
            from henrique.main.tool.entity.datetime.time.coloned.time_coloned import TimeColoned
            yield from TimeColoned.str2entity_list(s) or []

            from henrique.main.tool.entity.datetime.time.digits.time_digits import TimeDigits
            yield from TimeDigits.str2entity_list(s, is_focused) or []

            from henrique.main.tool.entity.datetime.time.standalone.time_standalone import TimeStandalone
            yield from TimeStandalone.str2entity_list(s) or []


        entity_list_raw = lfilter(bool, entity_iter())
        span_list_raw = lmap(FoxylibEntity.entity2span, entity_list_raw)
        index_list_uncovered = SpanTool.span_list2index_list_uncovered(span_list_raw)
        entity_list = lmap(lambda i: entity_list_raw[i], index_list_uncovered)

        return entity_list

    @classmethod
    def hour2norm_24(cls, h_in, ampm=None):
        if not 0 <= h_in <= 24:
            return None

        if ampm is None:
            return h_in % 24

        if not 0 <= h_in <= 12:
            return None

        if ampm in [AMPM.AM]:
            return h_in % 12

        assert_equal(ampm, AMPM.PM)
        return (h_in % 12) + 12









warmer.warmup()
