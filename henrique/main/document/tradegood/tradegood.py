from itertools import chain

from foxylib.tools.collections.collections_tool import luniq
from foxylib.tools.collections.iter_tool import IterTool
from foxylib.tools.json.json_tool import JsonTool


class Tradegood:
    class Field:
        CODENAME = "codename"
        ALIASES = "aliases"
        TRADEGOODTYPE = "tradegoodtype"

    @classmethod
    def _dict_codename2tradegood_all(cls):
        from henrique.main.document.tradegood.googlesheets.tradegood_googlesheets import TradegoodGooglesheets
        return TradegoodGooglesheets.dict_codename2tradegood()

    @classmethod
    def list_all(cls):
        return list(cls._dict_codename2tradegood_all().values())

    @classmethod
    def tradegood2codename(cls, tradegood):
        return tradegood[cls.Field.CODENAME]

    @classmethod
    def tradegood2tradegoodtype(cls, tradegood):
        return tradegood.get(cls.Field.TRADEGOODTYPE)

    @classmethod
    def tradegood_lang2aliases(cls, tradegood, lang):
        return JsonTool.down(tradegood, [cls.Field.ALIASES, lang])

    @classmethod
    def tradegood_langs2aliases(cls, tradegood, langs):
        return luniq(chain(*[cls.tradegood_lang2aliases(tradegood, lang) for lang in langs]))


    @classmethod
    def tradegood_lang2name(cls, tradegood, lang):
        return IterTool.first(cls.tradegood_lang2aliases(tradegood, lang))

    @classmethod
    def codename2tradegood(cls, codename):
        return cls._dict_codename2tradegood_all().get(codename)


