import logging

import psycopg2

from foxylib.tools.env.env_tools import EnvToolkit
from henrique.main.hub.logger.logger import HenriqueLogger


class PostgresHub:
    class Env:
        HOST = "POSTGRES_HOST"
        PORT = "POSTGRES_PORT"
        USER = "POSTGRES_USER"
        PASSWORD = "POSTGRES_PASSWORD"
        DBNAME = "POSTGRES_DBNAME"


    @classmethod
    def conn(cls):
        logger = HenriqueLogger.func_level2logger(cls.conn, logging.DEBUG)

        host = EnvToolkit.k2v(cls.Env.HOST)
        port = EnvToolkit.k2v(cls.Env.PORT)
        user = EnvToolkit.k2v(cls.Env.USER)
        password = EnvToolkit.k2v(cls.Env.PASSWORD)
        dbname = EnvToolkit.k2v(cls.Env.DBNAME)

        j_connect = {"host":host, "port":port, "user":user, "password":password, "dbname":dbname, }
        logger.debug({"j_connect":j_connect})
        conn = psycopg2.connect(**j_connect)
        return conn

    @classmethod
    def cursor(cls):
        with cls.conn() as conn:
            return conn.cursor()
