from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool


class HenriqueEntity:
    @classmethod
    def classes(cls):
        from henrique.main.entity.port.port_entity import PortEntity

        from henrique.main.entity.command.command_entity import CommandEntity
        from henrique.main.entity.tradegood.tradegood_entity import TradegoodEntity
        from henrique.main.entity.markettrend.trend_entity import MarkettrendEntity

        h = {CommandEntity,
             PortEntity,
             TradegoodEntity,
             MarkettrendEntity,
             }
        return h

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _h_type2class(cls):
        h = merge_dicts([{clazz.TYPE: clazz} for clazz in cls.classes()],
                        vwrite=vwrite_no_duplicate_key)
        return h

    @classmethod
    def entity_type2class(cls, entity_type):
        h = cls._h_type2class()
        return h.get(entity_type)
