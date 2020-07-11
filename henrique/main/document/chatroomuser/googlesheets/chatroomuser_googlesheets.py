import sys

from cachetools import LRUCache
from functools import lru_cache
from future.utils import lmap

from foxylib.tools.cache.cache_manager import CacheManager
from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key, DictTool, luniq
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.function.warmer import Warmer
from foxylib.tools.googleapi.sheets.googlesheets_tool import GooglesheetsTool
from henrique.main.document.chatroomuser.chatroomuser import Chatroomuser
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.google.googledoc.henrique_googleapi import HenriqueGoogleapi

MODULE = sys.modules[__name__]
WARMER = Warmer(MODULE)


class AliasesSheet:
    NAME = "aliases"

    @classmethod
    def dict_codename2aliases(cls):
        data_ll = ChatroomuserGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: luniq(row)} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class CommentsSheet:
    NAME = "comments"

    @classmethod
    def dict_codename2comments(cls):
        data_ll = ChatroomuserGooglesheets.sheetname2data_ll(cls.NAME)

        h = merge_dicts([{row[0]: row[1:]} for row in data_ll[1:]],
                        vwrite=vwrite_no_duplicate_key)
        return h


class ChatroomuserGooglesheets:
    @classmethod
    def shorturl(cls):
        return "https://bit.ly/2TRYkvi"

    @classmethod
    def spreadsheetId(cls):
        return "1HcW7Im6SWy2T8g6POFDTOQXzH1jeTBjPxJn7KZ3RHB4"

    @classmethod
    def _dict_sheetname2data_ll(cls, ):
        sheetname_list = [AliasesSheet.NAME, CommentsSheet.NAME,]
        return GooglesheetsTool.sheet_ranges2dict_range2data_ll(HenriqueGoogleapi.credentials(),
                                                                cls.spreadsheetId(),
                                                                sheetname_list,
                                                                )

    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=2),)
    def dict_sheetname2data_ll(cls,):
        return cls._dict_sheetname2data_ll()

    @classmethod
    def sheetname2data_ll(cls, sheetname):
        return cls.dict_sheetname2data_ll()[sheetname]

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_codename2chatroomuser(cls):
        chatroomuser_list_all = cls.chatroomuser_list_all()
        h = merge_dicts([{Chatroomuser.chatroomuser2codename(chatroomuser): chatroomuser} for chatroomuser in chatroomuser_list_all],
                        vwrite=DictTool.VWrite.f_vwrite2f_hvwrite(vwrite_no_duplicate_key),
                        )
        return h

    @classmethod
    @WARMER.add(cond=not HenriqueEnv.is_skip_warmup())
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def chatroomuser_list_all(cls):
        h_codename2aliases = AliasesSheet.dict_codename2aliases()
        h_codename2comments = CommentsSheet.dict_codename2comments()
        # raise Exception({"h_codename2product_list":h_codename2product_list})

        codename_list = list(h_codename2aliases.keys())

        def codename2chatroomuser(codename):
            aliases = h_codename2aliases.get(codename) or []
            comments = h_codename2comments.get(codename)

            chatroomuser = {Chatroomuser.Field.CODENAME: codename,
                            Chatroomuser.Field.COMMENTS: comments,
                            Chatroomuser.Field.ALIASES: aliases,
                            }
            return DictTool.filter(lambda k, v: v, chatroomuser)

        return lmap(codename2chatroomuser, codename_list)




# WARMER.warmup()
