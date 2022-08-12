from functools import wraps

from flask import request, abort

from config import Tokens
from utils.mongodb_wrap import MongoDB


def api_token_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        req_token = request.args.get('token')
        if not req_token == Tokens.API_TOKEN:
            uri = request.url
            status = 'error'
            message = 'wrong token'
            MongoDB().save_log(req_token, uri, message, status)
            abort(403)
        return func(*args, **kwargs)
    return decorator
