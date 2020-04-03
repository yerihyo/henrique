from nose.tools import assert_is_not_none

from foxylib.tools.collections.collections_tool import merge_dicts, vwrite_no_duplicate_key

from henrique.main.entity.port.mongodb.port_doc import PortDoc


class Price:
    class Field:
        PORT = "port"
        TRADEGOOD = "tradegood"
        RATE = "rate"
        TREND = "trend"

        @classmethod
        def set(cls):
            return {cls.PORT, cls.TRADEGOOD, cls.RATE, cls.TREND}

    class Trend:
        class Value:
            SKYRISE = "skyrise"
            RISE = "rise"
            AVERAGE = "average"
            DOWN = "down"
            PLUMMET = "plummet"

            @classmethod
            def list(cls):
                return [cls.PLUMMET, cls.DOWN, cls.AVERAGE, cls.RISE, cls.SKYRISE]

        @classmethod
        def trend2int(cls, trend):
            h = {cls.Value.SKYRISE: 2,
                 cls.Value.RISE: 1,
                 cls.Value.AVERAGE: 0,
                 cls.Value.DOWN: -1,
                 cls.Value.PLUMMET: -2,
                 }
            v = h.get(trend)
            assert_is_not_none(v)
            return v

        @classmethod
        def trend2arrow(cls, trend):
            h = {cls.Value.SKYRISE:'⇑',
                 cls.Value.RISE:'⇗',
                 cls.Value.AVERAGE:'⇒',
                 cls.Value.DOWN:'⇘',
                 cls.Value.PLUMMET:'⇓',
                 }
            arrow = h.get(trend)
            assert_is_not_none(arrow)
            return arrow


    @classmethod
    def key_default(cls, price):
        rate = Price.price2rate(price)
        v_trend = Price.Trend.trend2int(Price.price2trend(price))

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


class PriceDict:
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
            port_codename = Price.price2port(price)
            tradegood_codename = Price.price2tradegood(price)
            return port_codename, tradegood_codename

        price_dict = merge_dicts([{price2key(price): price} for price in price_list],
                                 vwrite=vwrite_no_duplicate_key)
        return price_dict

    @classmethod
    def lookup(cls, price_dict, port_codename, tradegood_codename):
        return price_dict[(port_codename, tradegood_codename)]

