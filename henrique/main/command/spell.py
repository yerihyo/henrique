from foxylib.tools.collections.iter_tool import IterTool


class Spell:
    class Field:
        TEXT = "text"
        LANG = "lang"
    F = Field

    @classmethod
    def j_command2text(cls, j_command):
        return j_command[cls.F.TEXT]


    @classmethod
    @IterTool.f_iter2f_list
    def query_lang2j_command_list(cls, query, lang):
        for str_line in query.splitlines():
            j_command = {cls.F.TEXT:str_line,
                         cls.F.LANG:lang,
                         }
            yield j_command
