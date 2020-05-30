import logging
from functools import lru_cache

from psycopg2.sql import Identifier, SQL

from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts
from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.uuid.uuid_tool import UUIDTool
from henrique.main.document.price.mongodb.marketprice_doc import MarketpriceDoc
from henrique.main.document.price.trend.trend_entity import Trend
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres
from khala.document.channel.channel import Channel
from khala.document.channel_user.channel_user import ChannelUser
from khala.singleton.logger.khala_logger import KhalaLogger
from khala.singleton.messenger.discord.external.channel.discord_channel import DiscordChannel
from khala.singleton.messenger.discord.internal.channel_user_discord import ChannelUserDiscord
from khala.singleton.messenger.kakaotalk.internal.channel_user_kakaotalk import ChannelUserKakaotalk


class ChatProgram:
    class Value:
        KAKAOTALK = 10
        DISCORD = 20

    @classmethod
    def program2channel(cls, program):
        h = {cls.Value.KAKAOTALK: Channel.Codename.KAKAOTALK_UWO,
             cls.Value.DISCORD: Channel.Codename.DISCORD,
             }
        return h[program]


class ChatuserTable:
    NAME = "foxyos_chatuser"

    class Field:
        PROGRAM = "program"
        KEY4PROGRAM = "key4program"
        NAME = "name"
        UUID = "uuid"

    @classmethod
    def row2program(cls, row):
        return row[cls.Field.PROGRAM]

    @classmethod
    def row2key4program(cls, row):
        return row[cls.Field.KEY4PROGRAM]

    @classmethod
    def row2name(cls, row):
        return row[cls.Field.NAME]

    @classmethod
    def row2uuid(cls, row):
        return row[cls.Field.UUID]

    @classmethod
    def _row_iter(cls):
        logger = KhalaLogger.func_level2logger(cls._row_iter, logging.DEBUG)

        # h_id2culture = CultureTable.dict_id2codename()
        # logger.debug({"h_id2culture":h_id2culture})

        h = {}
        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT * FROM {} ORDER BY id ASC").format(Identifier(cls.NAME), )
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                program, key4program, name, uuid_str = t[1:5]

                uiud_hex = UUIDTool.x2hex(uuid_str)

                yield {cls.Field.PROGRAM: program,
                       cls.Field.KEY4PROGRAM: key4program,
                       cls.Field.NAME: name,
                       cls.Field.UUID: uiud_hex,
                       }

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_uuid2row(cls,):
        row_list = list(cls._row_iter())

        h = merge_dicts([{(cls.row2uuid(row)): row}
                         for row in row_list],
                        vwrite=vwrite_no_duplicate_key)

        return h

    @classmethod
    def uuid2row(cls, uuid):
        return cls._dict_uuid2row().get(uuid)

    @classmethod
    def _row2channel_user_codename(cls, row):
        channel = ChatProgram.program2channel(cls.row2program(row))
        key4program = cls.row2key4program(row)

        if channel == Channel.Codename.DISCORD:
            return ChannelUserDiscord.id2codename(key4program)

        if channel == Channel.Codename.KAKAOTALK_UWO:
            return ChannelUserKakaotalk.sender_name2codename(key4program[2:])

        raise RuntimeError("Invalid channel: {}".format(channel))

    @classmethod
    def row2channel_user(cls, row, alias=None):
        channel = ChatProgram.program2channel(cls.row2program(row))
        codename = cls._row2channel_user_codename(row)

        channel_user = {ChannelUser.Field.CHANNEL: channel,
                        ChannelUser.Field.CODENAME: codename,
                        ChannelUser.Field.ALIAS: alias or cls.row2name(row),
                        }

        return channel_user
