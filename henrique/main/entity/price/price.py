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
    def price2port(cls, price):
        return price[cls.Field.PORT]

    @classmethod
    def price2tradegood(cls, price):
        return price[cls.Field.TRADEGOOD]


class PriceDict:
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

