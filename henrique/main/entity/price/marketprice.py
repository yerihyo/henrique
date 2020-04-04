from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key

from henrique.main.entity.port.mongodb.port_doc import PortDoc


class Marketprice:
    class Field:
        PORT = "port"
        TRADEGOOD = "tradegood"
        RATE = "rate"
        TREND = "trend"

        @classmethod
        def set(cls):
            return {cls.PORT, cls.TRADEGOOD, cls.RATE, cls.TREND}


    @classmethod
    def key_default(cls, price):
        rate = Marketprice.price2rate(price)
        v_trend = Marketprice.Trend.trend2int(Marketprice.price2trend(price))

        return -rate, -v_trend

    @classmethod
    def price2port(cls, price):
        return price[cls.Field.PORT]

    @classmethod
    def price2tradegood(cls, price):
        return price[cls.Field.TRADEGOOD]

    @classmethod
    def price2rate(cls, price):
        return price[cls.Field.RATE]

    @classmethod
    def price2trend(cls, price):
        return price[cls.Field.TREND]


class MarketpriceDict:
    @classmethod
    def ports_tradegoods2price_dict(cls, port_codenames, tradegood_codenames):
        from henrique.main.entity.price.mongodb.markettrend_doc import MarkettrendDoc
        prices_latest = MarkettrendDoc.ports_tradegoods2price_list_latest(port_codenames, tradegood_codenames)
        price_dict = cls.prices2price_dict(prices_latest)
        return price_dict

    @classmethod
    def prices2price_dict(cls, prices):
        price_list = list(prices)

        def price2key(price):
            port_codename = Marketprice.price2port(price)
            tradegood_codename = Marketprice.price2tradegood(price)
            return port_codename, tradegood_codename

        price_dict = merge_dicts([{price2key(price): price} for price in price_list],
                                 vwrite=vwrite_no_duplicate_key)
        return price_dict

    @classmethod
    def lookup(cls, price_dict, port_codename, tradegood_codename):
        return price_dict[(port_codename, tradegood_codename)]

