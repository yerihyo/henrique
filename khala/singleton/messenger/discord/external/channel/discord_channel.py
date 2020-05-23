from cachetools import LRUCache, cachedmethod

from foxylib.tools.cache.cache_manager import CacheManager
from khala.singleton.messenger.discord.external.client.discord_client import DiscordClient


class DiscordChannelCache:
    class Constant:
        MAXSIZE = 256


class DiscordChannel:
    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=DiscordChannelCache.Constant.MAXSIZE),)
    def id2channel(cls, channel_id):
        client = DiscordClient.client()
        return client.get_channel(channel_id)


    @classmethod
    def add_channel2cache(cls, channel):
        CacheManager.add2cache(cls.id2channel, channel, [channel.id])
