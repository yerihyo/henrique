import logging
import os
import sys

from foxylib.tools.file.file_tool import FileTool
from foxylib.tools.log.logger_tool import FoxylibLogger, LoggerTool
from functools import reduce, lru_cache

FILE_PATH = os.path.realpath(__file__)
REPO_DIR = reduce(lambda x,f:f(x), [os.path.dirname]*3, FILE_PATH)
LOG_DIR = os.path.join(REPO_DIR,"log")

class HenriqueLogger:
    ROOTNAME = "henrique"
    level = logging.DEBUG

    @classmethod
    def dirpath(cls): return LOG_DIR

    @classmethod
    def _rootname_list(cls):
        return FoxylibLogger.rootname_list() + [cls.ROOTNAME]

    @classmethod
    def attach_handler2loggers(cls, handler):
        for rootname in cls._rootname_list():
            logger = logging.getLogger(rootname)
            LoggerTool.add_or_skip_handlers(logger, [handler])

    @classmethod
    @lru_cache(maxsize=None)
    def attach_filepath2loggers(cls, filepath):
        FileTool.dirpath2mkdirs(os.path.dirname(filepath))
        handler = LoggerTool.handler2formatted(LoggerTool.filepath2handler_default(filepath))
        handler.setLevel(cls.level)
        cls.attach_handler2loggers(handler)

    @classmethod
    @lru_cache(maxsize=2)
    def attach_stderr2loggers(cls,):
        handler = LoggerTool.handler2formatted(logging.StreamHandler(sys.stderr))
        handler.setLevel(cls.level)
        cls.attach_handler2loggers(handler)


    @classmethod
    def func2name(cls, func):
        return LoggerTool.rootname_func2name(cls.ROOTNAME, func)

    @classmethod
    def func2logger(cls, func):
        return cls.func_level2logger(func, cls.level)

    @classmethod
    def func_level2logger(cls, func, level):
        logger = logging.getLogger(cls.func2name(func))
        logger.setLevel(level)
        return logger

    @classmethod
    def filename2logger(cls, filename):
        logger = LoggerTool.rootname_filename2logger(cls.ROOTNAME, filename)
        logger.setLevel(cls.level)
        return logger
