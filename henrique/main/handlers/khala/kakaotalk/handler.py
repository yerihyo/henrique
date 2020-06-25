import logging
import os

from flask import request

from foxylib.tools.entity.entity_tool import FoxylibEntity
from henrique.main.document.port.port_entity import PortEntity
from henrique.main.document.skill.skill_entity import HenriqueSkill
from henrique.main.document.tradegood.tradegood_entity import TradegoodEntity
from henrique.main.singleton.error.henrique_error import ErrorhandlerKakaotalk
from henrique.main.singleton.flask.henrique_urlpath import HenriqueUrlpath
from henrique.main.singleton.khala.henrique_khala import HenriquePacket, HenriqueCommand
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import Chatroom
from khala.document.packet.packet import KhalaPacket
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk
from khala.singleton.messenger.kakaotalk.internal.chatroom_kakaotalk import ChatroomKakaotalk

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)


class KakaotalkUWOHandler:
    class Data:
        class Field:
            TEXT = "text"
            SENDER_NAME = "sender_name"
            NEWLINE = "newline"

    @classmethod
    def url(cls):
        return HenriqueUrlpath.obj2url(cls.get)

    @classmethod
    def packet2skip_response(cls, packet):
        return False

        skill_code = HenriqueCommand.packet2skill_code(packet)

        if skill_code == HenriqueSkill.Codename.PRICE:
            return True

        text_in = KhalaPacket.packet2text(packet)
        config = HenriqueEntity.Config.packet2config(packet)

        if skill_code == HenriqueSkill.Codename.PORT:
            entity_list_port = PortEntity.text2entity_list(text_in, config=config)
            return bool(entity_list_port)

        if skill_code == HenriqueSkill.Codename.TRADEGOOD:
            entity_list_tradegood = TradegoodEntity.text2entity_list(text_in, config=config)
            return bool(entity_list_tradegood)

        return False

    @classmethod
    @ErrorhandlerKakaotalk.Decorator.error_handler
    def get(cls):
        logger = HenriqueLogger.func_level2logger(cls.get, logging.DEBUG)

        sender_name = request.args.get(cls.Data.Field.SENDER_NAME)
        text_in = request.args.get(cls.Data.Field.TEXT)
        newline = request.args.get(cls.Data.Field.NEWLINE)
        logger.debug({"sender_name":sender_name, "text_in":text_in, "newline":newline})

        if not HenriqueCommand.text2is_query(text_in):
            return None

        chatroom = ChatroomKakaotalk.chatroom()
        Chatroom.chatrooms2upsert([chatroom])

        channel_user = ChannelUserKakaotalk.sender_name2channel_user(sender_name)
        ChannelUser.channel_users2upsert([channel_user])

        packet = {KhalaPacket.Field.TEXT: text_in,
                  KhalaPacket.Field.CHATROOM: Chatroom.chatroom2codename(chatroom),
                  KhalaPacket.Field.CHANNEL_USER: ChannelUser.channel_user2codename(channel_user),
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }
        logger.debug({"packet": packet,})

        text_response = HenriquePacket.packet2response(packet)
        if not text_response:
            return None

        if cls.packet2skip_response(packet):  # run packet but do not respond
            return None

        text_out = newline.join(text_response.splitlines()) if newline else text_response

        return text_out, 200
