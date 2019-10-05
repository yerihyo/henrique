import re

from future.utils import lmap

from foxylib.tools.database.mongodb.mongodb_tools import MongoDBToolkit
from foxylib.tools.json.json_tools import jdown
from foxylib.tools.regex.regex_tools import RegexToolkit
from henrique.main.hub.mongodb.mongodb_hub import MongoDBHub



class PortCollection:
    NAME = "port"

    class Field:
        USER_ID = "user_id"
        DOC_ID = "doc_id"
        SPAN = "span"

    F = Field

    @classmethod
    def collection(cls, *_, **__):
        db = MongoDBHub.db()
        return db.get_collection(cls.NAME, *_, **__)


class PortDocument:
    @classmethod
    def jpath_name_en(cls): return ["name", "en"]

    @classmethod
    def jpath_name_ko(cls): return ["name", "ko"]

    @classmethod
    def j_iter(cls):
        collection = PortCollection.collection()
        yield from MongoDBToolkit.find_result2j_iter(collection.find({}))

    @classmethod
    def pattern(cls):
        jpath_list = [cls.jpath_name_en(), cls.jpath_name_ko()]

        j_list = list(cls.j_iter())
        name_list = [jdown(j, jpath)
                     for j in j_list
                     for jpath in jpath_list]

        rstr = RegexToolkit.rstr_list2or(lmap(re.escape,name_list))
        return re.compile(rstr, re.I)





class PortTable:
    NAME = "unchartedwatersonline_port"

    @classmethod
    def index_json(cls): return 2

