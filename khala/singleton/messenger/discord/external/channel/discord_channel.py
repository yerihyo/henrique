from cachetools import LRUCache, cachedmethod

from foxylib.tools.cache.cache_manager import CacheManager
from khala.singleton.messenger.discord.external.client.discord_client import DiscordClient


class DiscordChannelCache:
    class Constant:
        MAXSIZE = 256


class DiscordChannel:
    @classmethod
    @CacheManager.attach2method(self2cache=lambda x: LRUCache(maxsize=DiscordChannelCache.Constant.MAXSIZE), )
    @CacheManager.cachedmethod2use_manager(cachedmethod=cachedmethod)
    def id2channel(cls, channel_id):
        client = DiscordClient.client()
        return client.get_channel(channel_id)


    @classmethod
    def add_channel2cache(cls, channel):
        manager = CacheManager.callable2manager(cls.id2channel)
        CacheManager.add2cache(manager, channel, [channel.id])
