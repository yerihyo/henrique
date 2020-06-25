
class HenriqueLocale:
    DEFAULT = "ko-KR"

    @classmethod
    def langs(cls):
        return {"ko","en"}

    @classmethod
    def lang_count(cls):
        return len(cls.langs())

    @classmethod
    def lang2langs_recognizable(cls, lang):
        if lang == "en":
            return ["en"]

        return [lang, "en"]

    @classmethod
    def lang2tzdb(cls, lang):
        if lang == "ko":
            return "Asia/Seoul"

        if lang == "en":
            return "America/Los_Angeles"

        raise NotImplementedError({"lang":lang})
