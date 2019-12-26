class SkillnoteTool:
    class Field:
        SPELL = "spell"
        RESULT = "result"
    F = Field

    @classmethod
    def j2spell(cls, j):
        return j[SkillnoteTool.F.SPELL]

    @classmethod
    def j2result(cls, j):
        return j[cls.F.RESULT]
