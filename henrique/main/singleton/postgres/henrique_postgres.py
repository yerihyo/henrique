import logging

import psycopg2

from foxylib.tools.env.env_tool import EnvTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.logger.henrique_logger import HenriqueLogger


class HenriquePostgres:
    class Env:
        HOST = "POSTGRES_HOST"
        PORT = "POSTGRES_PORT"
        USER = "POSTGRES_USER"
        PASSWORD = "POSTGRES_PASSWORD"
        DBNAME = "POSTGRES_DBNAME"


    @classmethod
    def conn(cls):
        logger = HenriqueLogger.func_level2logger(cls.conn, logging.DEBUG)

        host = HenriqueEnv.key2value(cls.Env.HOST)
        port = HenriqueEnv.key2value(cls.Env.PORT)
        user = HenriqueEnv.key2value(cls.Env.USER)
        password = HenriqueEnv.key2value(cls.Env.PASSWORD)
        dbname = HenriqueEnv.key2value(cls.Env.DBNAME)

        j_connect = {"host":host, "port":port, "user":user, "password":password, "dbname":dbname, }
        logger.debug({"j_connect":j_connect})
        conn = psycopg2.connect(**j_connect)
        return conn

    @classmethod
    def cursor(cls):
        with cls.conn() as conn:
            return conn.cursor()
