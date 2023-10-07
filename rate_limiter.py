import time
from flask import request, make_response, jsonify
from redis import Redis
from functools import wraps

redis_instance = Redis(host='127.0.0.1', port=6379)

def rate_limit(limit: int, per: int, scope_func):
    """Rate limit decorator
    :param limit: Number of requests allowed per `per` seconds
    :param per: Number of seconds for `limit`
    :param scope_func: Function to get the scope of the request"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"rate-limit:{scope_func()}:{time.time() // per}"

            if redis_instance.get(key) is not None and int(redis_instance.get(key)) >= limit:
                return make_response(jsonify({'message': 'Too many requests'}), 429)

            else:
                redis_instance.incr(key, 1)
                redis_instance.expire(key, per)
                return f(*args, **kwargs)

        return decorated_function
    return decorator