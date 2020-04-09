from itertools import chain

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts, lchain
from functools import lru_cache

from foxylib.tools.function.function_tool import FunctionTool



class Entity:
    class Field:
        TYPE = "type"
        TEXT = "text"
        SPAN = "span"
        VALUE = "value"

    class Step:
        PRECISION = "precision"
        RECALL = "recall"

    class Config:
        class Field:
            LOCALE = "locale"
            STEP = "step"

        @classmethod
        def config2locale(cls, j):
            if not j:
                return None

            return j.get(cls.Field.LOCALE)

    @classmethod
    def entity2type(cls, entity):
        return entity[cls.Field.TYPE]

    @classmethod
    def entity2text(cls, entity):
        return entity[cls.Field.TEXT]

    @classmethod
    def entity2span(cls, entity):
        return entity[cls.Field.SPAN]

    @classmethod
    def entity2value(cls, entity):
        return entity[cls.Field.VALUE]

    @classmethod
    def text_extractors2entity_list(cls, text_in, entity_classes, config):
        entity_ll = [c.text2entity_list(text_in, config=config)
                     for c in entity_classes]
        entity_list = sorted(chain(*entity_ll), key=Entity.entity2span)
        return entity_list


class HenriqueEntity:
    class Cache:
        DEFAULT_SIZE = 100

    @classmethod
    def classes(cls):
        from henrique.main.document.port.port_entity import PortEntity

        from henrique.main.document.command.command_entity import CommandEntity
        from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
        from henrique.main.document.markettrend.trend_entity import MarkettrendEntity

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

    # @classmethod
    # def text_entity_class2entity_list(cls, text, entity_class):
    #     return entity_class.text2entity_list(text)

