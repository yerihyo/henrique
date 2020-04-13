import pytz
from datetime import datetime, timedelta
from future.utils import lmap
from nose.tools import assert_equal

from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.date.date_tools import DatetimeTool, TimedeltaTool


class HenriqueDatetime:
    class Constant:
        TIMEDELTA_OUTDATED = timedelta(days=2)

    @classmethod
    def timedelta_unit_list(cls):
        return [timedelta(days=1),
                timedelta(hours=1),
                timedelta(minutes=1),
                timedelta(seconds=1),
                ]

    @classmethod
    def lang2text_recent(cls, lang):
        return "방금전"

    @classmethod
    def value_unit_lang2text(cls, v, unit, lang):
        if lang != "ko":
            raise NotImplementedError({"lang":lang})

        if unit == timedelta(days=1):
            if v*unit >= cls.Constant.TIMEDELTA_OUTDATED:
                return "{}+일전".format(cls.Constant.TIMEDELTA_OUTDATED.days)
            else:
                return "{}일전".format(v)

        if unit == timedelta(hours=1):
            return "{}시간전".format(v)

        if unit == timedelta(minutes=1):
            return "{}분전".format(v)

        if unit == timedelta(seconds=1):
            return cls.lang2text_recent(lang)

        if unit is None:
            return cls.lang2text_recent(lang)

    @classmethod
    def timedelta_lang2str(cls, td, lang):
        unit_list = cls.timedelta_unit_list()
        index_unit = IterTool.value_units2index_largest_fit(td, lmap(lambda x: x * 2, unit_list))

        if index_unit is None:
            return cls.lang2text_recent(lang)

        unit = unit_list[index_unit]
        value = td // unit

        return cls.value_unit_lang2text(value, unit, lang)
