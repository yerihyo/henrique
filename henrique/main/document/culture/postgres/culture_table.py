from foxylib.tools.collections.collections_tool import vwrite_no_duplicate_key, merge_dicts

from foxylib.tools.database.postgres.postgres_tool import PostgresTool
from functools import lru_cache
from psycopg2.sql import SQL, Identifier

from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.postgres.henrique_postgres import HenriquePostgres


class CultureTable:
    NAME = "unchartedwatersonline_culture"

    @classmethod
    def index_json(cls):
        return 2

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def dict_id2codename(cls):
        with HenriquePostgres.cursor() as cursor:
            sql = SQL("SELECT id, name FROM {}").format(Identifier(cls.NAME), )
            cursor.execute(sql)

            h = merge_dicts([{id: codename}
                             for id, codename in PostgresTool.fetch_iter(cursor)],
                            vwrite=vwrite_no_duplicate_key)
        return h
