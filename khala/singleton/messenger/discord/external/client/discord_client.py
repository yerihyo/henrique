#!/usr/bin/env python3

import logging
import os

import discord
from functools import lru_cache, reduce

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.socialmedia.discord.discord_tool import DiscordTool
from khala.document.channel_user.channel_user import ChannelUser
from khala.document.chatroom.chatroom import Chatroom
from khala.singleton.logger.khala_logger import KhalaLogger
from khala.singleton.messenger.discord.internal.channel_user_discord import ChannelUserDiscord

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
REPO_DIR = reduce(lambda x, f: f(x), [os.path.dirname] * 5, FILE_DIR)


class DiscordClient:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def client(cls):
        client = discord.Client()
        client.event(cls.on_ready)
        client.event(cls.on_message)
        return client

    @classmethod
    async def on_ready(cls):
        logger = KhalaLogger.func_level2logger(cls.on_ready, logging.DEBUG)

        client = cls.client()
        logger.info({"client.user.name": client.user.name,
                     "client.user.id": client.user.id,
                     "client": client,
                     })

    @classmethod
    async def on_message(cls, message):
        from henrique.main.singleton.khala.henrique_khala import HenriqueKhala
        from khala.singleton.messenger.discord.internal.packet_discord import PacketDiscord
        from khala.singleton.messenger.discord.internal.chatroom_discord import ChatroomDiscord
        from henrique.main.singleton.khala.henrique_khala import HenriqueCommand

        logger = KhalaLogger.func_level2logger(cls.on_message, logging.DEBUG)
        client = cls.client()
        text_in = message.content

        logger.debug({"message": message, })

        if DiscordTool.user_message2is_author(client.user, message):
            return

        if not HenriqueCommand.text2is_query(text_in):
            return

        Chatroom.chatrooms2upsert([ChatroomDiscord.message2chatroom(message)])
        ChannelUser.channel_users2upsert([ChannelUserDiscord.message2channel_user(message)])

        packet = PacketDiscord.message2packet(message)
        logger.debug({"packet": packet, })

        text_out = HenriqueKhala.packet2response(packet)

        await message.channel.send(text_out)


def main():
    from henrique.main.singleton.logger.henrique_logger import KhalaLogger
    from henrique.main.singleton.env.henrique_env import HenriqueEnv

    KhalaLogger.attach_stderr2loggers(logging.DEBUG)
    KhalaLogger.attach_stderr2loggers(logging.DEBUG)

    # maybe update?
    # https://stackoverflow.com/a/50981577

    client = DiscordClient.client()
    discord_token = HenriqueEnv.key2value("DISCORD_TOKEN")
    client.run(discord_token)


if __name__ == "__main__":
    main()
