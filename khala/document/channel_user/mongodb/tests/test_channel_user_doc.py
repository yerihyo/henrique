import logging
from unittest import TestCase

from foxylib.tools.database.mongodb.mongodb_tool import MongoDBTool
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.skill.price.price_skill import PriceSkill
from khala.document.channel.channel import KakaotalkUWOChannel
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.channel_user.mongodb.channel_user_doc import ChannelUserDoc, ChannelUserCollection
from khala.document.chatroom.chatroom import KakaotalkUWOChatroom, Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.logger.khala_logger import KhalaLogger
from khala.singleton.messenger.discord.external.client.discord_client import DiscordClient
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk


class TestChannelUserDoc(TestCase):
    @classmethod
    def setUpClass(cls):
        HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    def test_01(self):
        Chatroom.chatrooms2upsert([ChatroomKakaotalk.chatroom()])

        sender_name = "iris"
        channel_user_codename = ChannelUserKakaotalk.sender_name2codename(sender_name)
        ChannelUser.channel_users2upsert([ChannelUserKakaotalk.sender_name2channel_user(sender_name)])

        # collection = ChannelUserCollection.collection()
        # collection.delete_one({ChannelUser.Field.CODENAME: channel_user_codename})

        packet = {KhalaPacket.Field.TEXT: "?price 육두구 리스본 120ㅅ",
                  KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.codename(),
                  KhalaPacket.Field.CHANNEL_USER: channel_user_codename,
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        PriceSkill.packet2response(packet)

        collection = ChannelUserCollection.collection()
        channel_user_doc = MongoDBTool.bson2json(collection.find_one({ChannelUser.Field.CODENAME: channel_user_codename}))
        hyp = MongoDBTool.doc2id_excluded(channel_user_doc,)
        ref = {'channel': 'kakaotalk_uwo',
               'codename': 'kakaotalk_uwo-iris',
               'alias': 'iris'}

        # pprint(hyp)
        self.assertEqual(hyp, ref)


