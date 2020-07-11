from flask import request
from functools import wraps, lru_cache

from foxylib.tools.function.function_tool import FunctionTool
from henrique.main.singleton.env.henrique_env import HenriqueEnv
from henrique.main.singleton.error.command_error import HenriqueCommandError
from henrique.main.singleton.socialmedia.slack.foxytrixy_server import ErrorsChannel


class ErrorhandlerKakaotalk:
    class Codename:
        COMMAND_ERROR = "COMMAND_ERROR"

    @classmethod
    @FunctionTool.wrapper2wraps_applied(lru_cache(maxsize=2))
    def _dict_codename2class(cls):
        from henrique.main.singleton.error.command_error import HenriqueCommandError
        return {cls.Codename.COMMAND_ERROR: HenriqueCommandError}

    @classmethod
    def codename2class(cls, codename):
        return cls._dict_codename2class().get(codename)

    class Decorator:
        @classmethod
        def error_handler(cls, func=None, default=None, exception_tuple=(Exception,),):
            if default is None:
                default = ("미안해요. 오류가 났어요.", 200)

            def wrapper(f):
                die_on_error = HenriqueEnv.key2nullboolean(HenriqueEnv.Key.DIE_ON_ERROR)
                # raise Exception(die_on_error)
                if die_on_error is True:
                    return f

                @wraps(f)
                def wrapped(*args, **kwargs):
                    try:
                        return f(*args,**kwargs)
                    except HenriqueCommandError as e:
                        return str(e)
                    except exception_tuple:
                        message = str({"request.args": request.args})
                        ErrorsChannel.post(message)
                        return default
                return wrapped

            return wrapper(func) if func else wrapper

