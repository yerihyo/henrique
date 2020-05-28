from flask import request
from functools import wraps

from henrique.main.singleton.socialmedia.slack.foxytrixy_server import ErrorsChannel


class ErrorhandlerKakaotalk:
    @classmethod
    def decorator_unknown_error_handler(cls, func=None, default=None, exception_tuple=(Exception,),):
        if default is None:
            default = ("미안해요. 오류가 났어요.", 200)

        def wrapper(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                try:
                    return f(*args,**kwargs)
                except exception_tuple:
                    message = str({"request.args": request.args})
                    ErrorsChannel.post(message)
                    return default
            return wrapped

        return wrapper(func) if func else wrapper

