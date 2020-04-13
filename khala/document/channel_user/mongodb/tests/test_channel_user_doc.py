import logging
from pprint import pprint
from unittest import TestCase

from pymongo.results import BulkWriteResult

from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc, ChannelUserCollection
from khala.document.chatroom.chatroom import Chatroom, KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket

from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class TestChannelUserDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        collection = ChannelUserCollection.collection()
        collection.delete_one({ChannelUserDoc.Field.CODENAME:"kakaotalk_uwo-iris"})

        packet = {KhalaPacket.Field.TEXT: "?price 육두구 리스본 120ㅅ",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
                  KhalaPacket.Field.CHANNEL_USER: KakaotalkUWOChannel.username2channel_user_codename("iris"),
                  KhalaPacket.Field.SENDER_NAME: "iris",
                  }
        ChannelUser.packet2upsert(packet)

        channel_user_doc = MongoDBTool.bson2json(collection.find_one({ChannelUserDoc.Field.CODENAME: "kakaotalk_uwo-iris"}))
        hyp = MongoDBTool.doc2id_excluded(channel_user_doc,)
        ref = {'channel': 'kakaotalk_uwo',
               'codename': 'kakaotalk_uwo-iris',
               'alias': 'iris'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)


