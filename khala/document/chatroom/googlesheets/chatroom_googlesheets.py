from functools import lru_cache

from future.utils import lfilter

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from foxylib.tools.string.string_tool import str2strip
from khala.document.chatroom.chatroom import Chatroom
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi


class ChatroomSheet:
    NAME = "chatroom"

    @classmethod
    def dict_codename2chatroom(cls):
        data_ll = ChatroomGooglesheets.sheetname2data_ll(cls.NAME)
        top_row = data_ll[0]

        def row2chatroom(row):
            chatroom = merge_dicts([{col_top: str2strip(row[i])}
                                    for i, col_top in enumerate(top_row)],
                                   vwrite=vwrite_no_duplicate_key)

            if not Chatroom.chatroom2codename(chatroom):
                return None

            return chatroom

        chatroom_list = lfilter(bool, map(row2chatroom, data_ll[1:]))
        h = merge_dicts([{Chatroom.chatroom2codename(chatroom): chatroom}
                         for chatroom in chatroom_list],
                        vwrite=vwrite_no_duplicate_key)

        return h


class ChatroomGooglesheets:
    @classmethod
    def spreadsheetId(cls):
        return "1b_BGWX2kPmXgObdk9vCLNqS6c39v1snHykEKDIWe46I"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=10))
    def sheetname2data_ll(cls, sheetname):
        data_ll = GooglesheetsTool.cred_id_name2data_ll(HenriqueGoogleapi.credentials(), cls.spreadsheetId(), sheetname)
        return data_ll

    @classmethod
    def dict_codename2chatroom(cls):
        h_codename2chatroom = ChatroomSheet.dict_codename2chatroom()
        return h_codename2chatroom
