import logging
from unittest import TestCase

from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc, ChannelUserCollection
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom
from khala.document.packet.packet import KhalaPacket


class TestChannelUserDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        collection = ChannelUserCollection.collection()
        collection.delete_one({ChannelUser.Field.CODENAME:"kakaotalk_uwo-iris"})

        packet = {KhalaPacket.Field.TEXT: "?price 육두구 리스본 120ㅅ",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: KakaotalkUWOChannel.username2channel_user_codename("iris"),
                  KhalaPacket.Field.SENDER_NAME: "iris",
                  }
        ChannelUser.packet2upsert(packet)

        channel_user_doc = MongoDBTool.bson2json(collection.find_one({ChannelUser.Field.CODENAME: "kakaotalk_uwo-iris"}))
        hyp = MongoDBTool.doc2id_excluded(channel_user_doc,)
        ref = {'channel': 'kakaotalk_uwo',
               'codename': 'kakaotalk_uwo-iris',
               'alias': 'iris'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)


