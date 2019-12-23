from future.utils import lfilter

from foxylib.tools.collections.collections_tool import IterTool


class Pousy:
    class Field:
        TEXT = "text"
        LANG = "lang"
    F = Field

    @classmethod
    def j_pousy2text(cls, j_pousy):
        return j_pousy[cls.F.TEXT]

    @classmethod
    def j_pousy2spell_list(cls, j_pousy):
        text = cls.j_pousy2text(j_pousy)
        return lfilter(bool, text.splitlines())


