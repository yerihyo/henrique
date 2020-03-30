from nose.tools import assert_equal

from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from psycopg2.sql import Identifier, SQL

from foxylib.tools.string.string_tool import str2lower
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres


class TradegoodTable:
    NAME = "unchartedwatersonline_tradegood"

    @classmethod
    def index_json(cls): return 2

    @classmethod
    def name_en_list2tradegood_id_list(cls, name_en_list):
        h = {}
        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT id, name_en from {}").format(Identifier(cls.NAME))
            cursor.execute(sql)

            for t in PostgresTool.fetch_iter(cursor):
                assert_equal(len(t), 2)
                h[str2lower(t[1])] = t[0]

        tradegood_id_list = [h.get(str2lower(name_en)) for name_en in name_en_list]
        return tradegood_id_list
