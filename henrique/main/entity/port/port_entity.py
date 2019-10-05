from foxylib.tools.collections.collections_tools import merge_dicts

from henrique.main.entity.entity import Entity
from henrique.main.hub.mongodb.port.port_collection import PortDocument


class PortEntity:
    NAME = "port"

    @classmethod
    def str2entity_list(cls, str_in):
        m_list = list(PortDocument.pattern().finditer(str_in))

        entity_list = [merge_dicts([Entity.F.match2h(m),
                                    Entity.F.type2h(cls.NAME),
                                    ])
                       for m in m_list]
        return entity_list


