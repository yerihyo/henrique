import logging

from itertools import chain

from foxylib.tools.collections.collections_tool import luniq
from nose.tools import assert_equal

from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from psycopg2.sql import Identifier, SQL

from foxylib.tools.json.json_tool import JsonTool
from foxylib.tools.string.string_tool import str2lower
from henrique.main.entity.culture.postgres.culture_table import CultureTable
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres

j = {"name": {"en": "Seville", "ko": "세비야"},
     "nicknames": {"ko": ["세비아", "세뱌", "세빌"]},
     "tradegoods": [
         {"name": {"en": "Wheat", "ko": "밀"}, "uuid": "aa06df1aa6a94cfe88db6106cdf0d141", "price": 39,
          "tradegoodtype": {"name": "Foodstuffs", "uuid": "ca5dd49acb054c4d81162fe7376d06bc"}},
         {"name": {"en": "Mercury Ointment", "ko": "수은제"}, "uuid": "a8c91ac7267349d3aa22720e623a46bb", "price": 1454,
          "tradegoodtype": {"name": "Medicine", "uuid": "5058a24a15684919aa88b1e3546b843c"}},
         {"name": {"en": "Wine", "ko": "와인"}, "uuid": "9a5ad9f3214e4cae9cd0e5b5f816c20b", "price": 429,
          "tradegoodtype": {"name": "Alcohol", "uuid": "5695c90999ec4cb1957622c2ed52923b"}},
         {"name": {"en": "Mercury", "ko": "수은"}, "uuid": "2acdaa1a89ce472997732a6a0e2f6471", "price": 1120,
          "tradegoodtype": {"name": "Wares", "uuid": "194f687b5ed44654b502511304514b8f"}},
         {"name": {"en": "Leatherwork", "ko": "피혁제품"}, "uuid": "9d5ff86254b04feeb109e11e2e2e3ccf", "price": 1153,
          "tradegoodtype": {"name": "Crafts", "uuid": "4ac335ae497c474ca6b45ef3db739e93"}},
         {"name": {"en": "Cotton Fabric", "ko": "면 원단"}, "uuid": "3aca5d44ca4d401e88644e3777072da6", "price": 761,
          "tradegoodtype": {"name": "Fabrics", "uuid": "3c8eda448cf84dc5b59821ca3df50278"}},
         {"name": {"en": "Muskets", "ko": "머스켓총"}, "uuid": "14a5ea4f475a4d3589c2357485801cff", "price": 2847,
          "tradegoodtype": {"name": "Firearms", "uuid": "165bf35f636e461fa6c2a927044e7292"}},
         {"name": {"en": "Shot", "ko": "탄환"}, "uuid": "220c0f42202a4272bdee46fe4eabe4ec", "price": 839,
          "tradegoodtype": {"name": "Firearms", "uuid": "165bf35f636e461fa6c2a927044e7292"}},
         {"name": {"en": "Arquebuses", "ko": "화승총"}, "uuid": "42bd8623e238424e8cf33600cb9f98ac", "price": 1906,
          "tradegoodtype": {"name": "Firearms", "uuid": "165bf35f636e461fa6c2a927044e7292"}},
         {"name": {"en": "Cannon", "ko": "대포"}, "uuid": "2599039aea7246ccb738c7f69e27898b", "price": 3237,
          "tradegoodtype": {"name": "Firearms", "uuid": "165bf35f636e461fa6c2a927044e7292"}}
     ]}

class PortData:
    @classmethod
    def data_lang2aliases_en(cls, data, lang):
        name_en = JsonTool.down(data, ["name",lang])
        nicknames_en = JsonTool.down(data, ["nicknames", lang]) or []
        return luniq(chain([name_en], nicknames_en))


class PortTable:
    NAME = "unchartedwatersonline_port"

    @classmethod
    def index_json(cls): return 2

    # @classmethod
    # def name_en_list2port_id_list(cls, name_en_list):
    #     h = {}
    #     with HenriquePostgres.cursor() as cursor:
    #         sql = SQL("SELECT id, name_en FROM {}").format(Identifier(cls.NAME), )
    #         cursor.execute(sql)
    #
    #         for t in PostgresTool.fetch_iter(cursor):
    #             assert_equal(len(t), 2)
    #             h[str2lower(t[1])] = t[0]
    #
    #
    #     port_id_list = [h.get(str2lower(name_en)) for name_en in name_en_list]
    #     return port_id_list

    @classmethod
    def codename_culture_iter(cls):
        logger = HenriqueLogger.func_level2logger(cls.codename_culture_iter, logging.DEBUG)

        h_id2culture = CultureTable.dict_id2codename()
        # logger.debug({"h_id2culture":h_id2culture})

        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT name_en, culture_id FROM {} ORDER BY id ASC").format(Identifier(cls.NAME), )
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                codename, culture_id = t
                codename_culture = h_id2culture[culture_id]
                yield (codename, codename_culture)

def main():
    HenriqueLogger.attach_stderr2loggers(logging.DEBUG)

    print("\n".join(map(",".join, PortTable.codename_culture_iter())))

if __name__ == '__main__':
    main()

