from foxylib.tools.collections.collections_tools import merge_dicts
from foxylib.tools.regex.regex_tools import MatchToolkit


class EntityTool:
    class Cache:
        DEFAULT_SIZE = 32

    class Field:
        TEXT = "text"
        TYPE = "type"
        SPAN = "span"
        VALUE = "value"
        EXTRA = "extra"

        @classmethod
        def text2h(cls, x): return {cls.TEXT: x}
        @classmethod
        def type2h(cls, x): return {cls.TYPE: x}
        @classmethod
        def span2h(cls, x): return {cls.SPAN: x}
        @classmethod
        def value2h(cls, x): return {cls.VALUE: x}
        @classmethod
        def extra2h(cls, x): return {cls.EXTRA: x}

        @classmethod
        def match2h(cls, m):
            span = MatchToolkit.match2span(m)
            text = MatchToolkit.match2text(m)

            l = [cls.span2h(span),
                 cls.text2h(text),
                 cls.value2h(text),
                 ]
            return merge_dicts(l)

        @classmethod
        def entity2text(cls, entity): return entity[cls.TEXT]
        @classmethod
        def entity2type(cls, entity): return entity[cls.TYPE]
        @classmethod
        def entity2span(cls, entity): return entity[cls.SPAN]
        @classmethod
        def entity2value(cls, entity): return entity.get(cls.VALUE, cls.entity2text(entity))
        @classmethod
        def entity2extra(cls, entity): return entity[cls.EXTRA]
        @classmethod
        def entity2start(cls, entity): return cls.entity2span(entity)[0]
        @classmethod
        def entity2end(cls, entity):return cls.entity2span(entity)[1]

    F = Field


