from itertools import chain

from foxylib.tools.collections.collections_tool import luniq
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.json.json_tool import JsonTool


class Tradegoodtype:
    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"
        CATEGORY = "category"

    @classmethod
    def _dict_codename2tradegoodtype_all(cls):
        from henrique.main.document.tradegoodtype.googlesheets.tradegoodtype_googlesheets import TradegoodtypeGooglesheets
        return TradegoodtypeGooglesheets.dict_codename2tradegoodtype()

    @classmethod
    def list_all(cls):
        return list(cls._dict_codename2tradegoodtype_all().values())

    @classmethod
    def tradegoodtype2codename(cls, tradegoodtype):
        return tradegoodtype[cls.Field.CODENAME]

    @classmethod
    def tradegoodtype2category(cls, tradegoodtype):
        return tradegoodtype[cls.Field.CATEGORY]

    @classmethod
    def tradegoodtype_lang2aliases(cls, tradegoodtype, lang):
        return JsonTool.down(tradegoodtype, [cls.Field.ALIASES, lang])

    @classmethod
    def tradegoodtype_langs2aliases(cls, tradegoodtype, langs):
        return luniq(chain(*[cls.tradegoodtype_lang2aliases(tradegoodtype, lang) for lang in langs]))


    @classmethod
    def tradegoodtype_lang2name(cls, tradegoodtype, lang):
        return IterTool.first(cls.tradegoodtype_lang2aliases(tradegoodtype, lang))

    @classmethod
    def codename2tradegoodtype(cls, codename):
        return cls._dict_codename2tradegoodtype_all().get(codename)
