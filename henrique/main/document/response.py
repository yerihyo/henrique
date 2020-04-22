class Response:
    class Field:
        TEXT = "text"
    F = Field

    @classmethod
    def str2j_response(cls, str_out):
        return {cls.F.TEXT:str_out}