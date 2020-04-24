#!/usr/bin/env python3

import logging
import os

import discord
from functools import lru_cache, reduce

from foxylib.tools.function.function_tool import FunctionTool
from foxylib.tools.socialmedia.discord.discord_tool import DiscordTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.khala.henrique_khala import HenriqueCommand
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger

FILE_PATH = os.path.realpath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
FILE_NAME = os.path.basename(FILE_PATH)
REPO_DIR = reduce(lambda x, f: f(x), [os.path.dirname] * 5, FILE_DIR)


class KhalaDiscordClient:
    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def client(cls):
        client = discord.Client()
        client.event(cls.on_ready)
        client.event(cls.on_message)
        return client

    @classmethod
    async def on_ready(cls):
        logger = HenriqueLogger.func_level2logger(cls.on_ready, logging.DEBUG)

        client = cls.client()
        logger.info({"client.user.name": client.user.name,
                     "client.user.id": client.user.id,
                     "client": client,
                     })

    @classmethod
    def text2is_related(cls, text):
        return bool(HenriqueCommand.pattern_prefix().match(text))

    @classmethod
    async def on_message(cls, message):
        logger = HenriqueLogger.func_level2logger(cls.on_message, logging.DEBUG)
        client = cls.client()
        text_in = message.content

        logger.debug({"message": message, })

        if DiscordTool.user_message2is_author(client.user, message):
            return

        if not cls.text2is_related(text_in):
            return

        # packet = {KhalaPacket.Field.TEXT: message.content,
        #           KhalaPacket.Field.CHATROOM: KakaotalkUWOChatroom.CODENAME,
        #           KhalaPacket.Field.CHANNEL_USER: KakaotalkUWOChannel.username2channel_user_codename("iris"),
        #           KhalaPacket.Field.SENDER_NAME: "iris",
        #           }
        # text_out = HenriqueKhala.packet2response(packet)

        text_out = text_in
        await message.channel.send(text_out)


def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    client = KhalaDiscordClient.client()
    discord_token = HenriqueEnv.key2value("DISCORD_TOKEN")
    client.run(discord_token)

if __name__ == "__main__":
    main()
