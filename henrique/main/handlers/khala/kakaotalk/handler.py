import os

from flask import request

from henrique.main.singleton.flask.henrique_urlpath import HenriqueUrlpath
from henrique.main.singleton.khala.henrique_khala import HenriqueKhala, HenriqueCommand
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
    # @app.route(UrlpathTool.filepath_pair2url(FILE_DIR, FRONT_DIR))
    def get(cls):
        sender_name = request.args.get(cls.Data.Field.SENDER_NAME)
        text_in = request.args.get(cls.Data.Field.TEXT)
        newline = request.args.get(cls.Data.Field.NEWLINE)

        if not HenriqueCommand.text2is_query(text_in):
            return

        chatroom = ChatroomKakaotalk.chatroom()
        Chatroom.chatrooms2upsert([chatroom])

        channel_user = ChannelUserKakaotalk.sender_name2channel_user(sender_name)
        ChannelUser.channel_users2upsert([channel_user])

        packet = {KhalaPacket.Field.TEXT: text_in,
                  KhalaPacket.Field.CHATROOM: Chatroom.chatroom2codename(chatroom),
                  KhalaPacket.Field.CHANNEL_USER: ChannelUser.channel_user2codename(channel_user),
                  KhalaPacket.Field.SENDER_NAME: sender_name,
                  }

        text_response = HenriqueKhala.packet2response(packet)

        text_out = newline.join(text_response.splitlines()) if newline else text_response

        return text_out, 200
