from functools import lru_cache
from future.utils import lmap

from foxylib.tools.collections.collections_tool import DictTool
from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.mongodb.henrique_mongodb import HenriqueMongodb
from khala.document.channel.channel import Channel
from khala.document.chatroom.chatroom import Chatroom

# MODULE = sys.modules[__name__]
# WARMER = Warmer(MODULE)
from khala.document.packet.packet import KhalaPacket


class ChatroomCollection:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def collection(cls, *_, **__):
        db = HenriqueMongodb.db()
        return db.get_collection("chatroom", *_, **__)


class ChatroomDoc:

    @classmethod
    def docs2upsert(cls, docs):
        def doc2pair(doc):
            doc_filter = DictTool.keys2filtered(doc, [Chatroom.Field.CODENAME])
            return (doc_filter, doc)

        pair_list = lmap(doc2pair, docs)

        collection = ChatroomCollection.collection()
        mongo_result = MongoDBTool.j_pair_list2upsert(collection, pair_list)
        return mongo_result

