from functools import lru_cache

from foxylib.tools.collections.collections_tool import l_singleton2obj, lchain
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.entity.command.command_entity import CommandEntity
from henrique.main.entity.henrique_entity import HenriqueEntity, Entity
from henrique.main.skill.henrique_skill import HenriqueSkill
from khalalib.packet.packet import KhalaPacket


# class Breakdown:
# class Analysis:
# class Parse:
# class Interpret:
# class Inspection:
# class Anatomy:
#     def __init__(self, packet):
#         self.packet = packet
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def text(self):
#         return KhalaPacket.packet2text(self.packet)
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def entity_command(self):
#         text = self.text()
#         entity_list = CommandEntity.text2entity_list(text)
#         return l_singleton2obj(entity_list)
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
#     def skill_code(self):
#         entity_command = self.entity_command()
#         if entity_command is None:
#             return None
#
#         skill_code = Entity.entity2value(entity_command)
#         return skill_code
#
#     @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=None))
#     def entity_class2entity_list(self, entity_class):
#         return entity_class.text2entity_list(self.text())


class HenriqueKhala:
    @classmethod
    def packet2response(cls, packet):
        text = KhalaPacket.packet2text(packet)
        skill_code = CommandEntity.text2skill_code(text)

        skill_class = HenriqueSkill.codename2class(skill_code)
        response = skill_class.packet2response(packet)
        return response

