from future.utils import lfilter

from foxylib.tools.string.string_tool import str2strip, StringTool
from khala.document.packet.packet import KhalaPacket


class HenriqueKhala:
    @classmethod
    def packet2response(cls, packet):
        from henrique.main.document.skill.skill_entity import SkillEntity, HenriqueSkill

        text = KhalaPacket.packet2text(packet)
        skill_code = SkillEntity.text2skill_code(text)

        skill_class = HenriqueSkill.codename2class(skill_code)
        response_raw = skill_class.packet2response(packet)
        return Rowsblock.text2norm(response_raw)


class Rowsblock:
    @classmethod
    def rows2text(cls, rows):
        return "\n".join(lfilter(bool, map(str2strip, rows)))

    @classmethod
    def blocks2text(cls, blocks):
        return "\n\n".join(lfilter(bool, map(str2strip, blocks)))

    @classmethod
    def text2norm(cls, text_in):
        if not text_in:
            return text_in

        text_out = StringTool.str2strip_eachline(StringTool.str2strip(text_in))
        return text_out
