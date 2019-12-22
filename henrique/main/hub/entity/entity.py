from foxylib.tools.collections.collections_tool import merge_dicts
from foxylib.tools.regex.regex_tool import MatchTool


class Entity:
    class Cache:
        DEFAULT_SIZE = 32

    class Field:
        TEXT = "text"
        TYPE = "type"
        SPAN = "span"
        VALUE = "value"
        EXTRA = "extra"
    F = Field

    class Builder:
        @classmethod
        def text2h(cls, x): return {Entity.F.TEXT: x}
        @classmethod
        def type2h(cls, x): return {Entity.F.TYPE: x}
        @classmethod
        def span2h(cls, x): return {Entity.F.SPAN: x}
        @classmethod
        def value2h(cls, x): return {Entity.F.VALUE: x}
        @classmethod
        def extra2h(cls, x): return {Entity.F.EXTRA: x}

        @classmethod
        def match2h(cls, m):
            span = MatchTool.match2span(m)
            text = MatchTool.match2text(m)

            l = [cls.span2h(span),
                 cls.text2h(text),
                 cls.value2h(text),
                 ]
            return merge_dicts(l)



    @classmethod
    def entity2text(cls, entity): return entity[cls.F.TEXT]
    @classmethod
    def entity2type(cls, entity): return entity[cls.F.TYPE]
    @classmethod
    def entity2span(cls, entity): return entity[cls.F.SPAN]
    @classmethod
    def entity2value(cls, entity): return entity.get(cls.F.VALUE, cls.entity2text(entity))
    @classmethod
    def entity2extra(cls, entity): return entity[cls.F.EXTRA]
    @classmethod
    def entity2start(cls, entity): return cls.entity2span(entity)[0]
    @classmethod
    def entity2end(cls, entity):return cls.entity2span(entity)[1]




