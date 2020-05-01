from cachetools import LRUCache, cached
from cachetools.keys import hashkey
from functools import partial

from foxylib.tools.cache.cachetools.cachetools_tool import CachetoolsTool, CachetoolsManager
from khala.singleton.messenger.discord.external.channel.discord_channel import DiscordChannel


class DiscordMessageCache:
    class Constant:
        MAXSIZE = 256


class DiscordMessage:
    @classmethod
    @CachetoolsManager.attach2func(key=CachetoolsTool.key4classmethod(hashkey),
                                   cache=LRUCache(maxsize=DiscordMessageCache.Constant.MAXSIZE),
                                   )
    def id2message(cls, channel_id, message_id):
        channel = DiscordChannel.id2channel(channel_id)
        return channel.messages.fetch(message_id)


    @classmethod
    def add_message2cache(cls, message):
        channel = message.channel
        DiscordChannel.add_channel2cache(channel)
        cls.id2message.cachetools_manager.add2cache(message, [cls, channel.id, message.id])
