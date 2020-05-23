from cachetools import LRUCache, cachedmethod

from foxylib.tools.cache.cache_manager import CacheManager
from khala.singleton.messenger.discord.external.channel.discord_channel import DiscordChannel


class DiscordMessageCache:
    class Constant:
        MAXSIZE = 256


class DiscordMessage:
    @classmethod
    @CacheManager.attach_cachedmethod(self2cache=lambda x: LRUCache(maxsize=DiscordMessageCache.Constant.MAXSIZE),
                                      )
    def id2message(cls, channel_id, message_id):
        channel = DiscordChannel.id2channel(channel_id)
        return channel.messages.fetch(message_id)

    @classmethod
    def add_message2cache(cls, message):
        channel = message.channel
        DiscordChannel.add_channel2cache(channel)
        CacheManager.add2cache(cls.id2message, message, [channel.id, message.id])
