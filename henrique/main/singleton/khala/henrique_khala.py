from functools import lru_cache

from foxylib.tools.collections.collections_tool import l_singleton2obj, lchain
from foxylib.tools.entity.entity_tool import Entity
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.entity.command.command_entity import CommandEntity
from henrique.main.entity.henrique_entity import HenriqueEntity
from henrique.main.skill.henrique_skill import HenriqueSkill
from khalalib.packet.packet import KhalaPacket


# class Breakdown:
# class Anatomy:
# class Analysis:
# class Parse:
# class Interpret:
# class Inspection:
class Anatomy:
    def __init__(self, packet):
        self.packet = packet

    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def text(self):
        return KhalaPacket.packet2text(self.packet)

    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def entity_command(self):
        text = self.text()
        entity_list = CommandEntity.text2entity_list(text)
        return l_singleton2obj(entity_list)

    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def skill_name(self):
        entity_command = self.entity_command()
        if entity_command is None:
            return None

        skill_name = Entity.entity2value(entity_command)
        return skill_name

    def entity_types2entity_list(self, entity_types):
        entity_ll = filter(bool, map(self.entity_type2entity_list, entity_types))
        return lchain(*entity_ll)

    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=None))
    def entity_type2entity_list(self, entity_type):
        clazz = HenriqueEntity.entity_type2class(entity_type)
        if not clazz:
            return None

        return clazz.text2entity_list(self.text())

    @classmethod
    def packet2response(cls, packet):
        anatomy = cls(packet)
        skill_name = anatomy.skill_name()
        skill_class = HenriqueSkill.name2class(skill_name)
        response = skill_class.anatomy2response(anatomy)
        return response


# class HenriqueKhala:
#     @classmethod
#     def packet2skill(cls, packet):
#         pass
#
#     @classmethod
#     def packet2response(cls, packet):
#         anatomy = Anatomy(packet)
#
#         text = KhalaPacket.packet2text(packet)
#
#
#         j_chat = KhalaPacket.j_packet2j_chat(packet)
#         text_body = KhalaPacket.chat2text_body(j_chat)
#
#         # l = str2split(text_body)
#         if not text_body:
#             return None
#
#         action_list = [PortSkill]
#
#         action_list_matched = lfilter(lambda x: x.text_body2match(text_body), action_list)
#         if not action_list_matched:
#             return None
#
#         if len(action_list_matched) > 1:
#             return None
#
#         return action_list_matched[0]

