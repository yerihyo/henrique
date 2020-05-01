from cachetools import LRUCache, cached
from cachetools.keys import hashkey
from functools import partial

from foxylib.tools.cache.cachetools.cachetools_tool import CachetoolsTool, CachetoolsManager
from khala.singleton.messenger.discord.external.client.discord_client import DiscordClient


class DiscordChannelCache:
    class Constant:
        MAXSIZE = 256


class DiscordChannel:
    @classmethod
    @CachetoolsManager.attach2func(key=CachetoolsTool.key4classmethod(hashkey),
                                   cache=LRUCache(maxsize=DiscordChannelCache.Constant.MAXSIZE),
                                   )
    def id2channel(cls, channel_id):
        client = DiscordClient.client()
        return client.get_channel(channel_id)


    @classmethod
    def add_channel2cache(cls, channel):
        cls.id2channel.cachetools_manager.add2cache(channel, [cls, channel.id])
