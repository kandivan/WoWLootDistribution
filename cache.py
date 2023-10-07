import redis
from functools import wraps

# Initialize Redis
cache = redis.Redis(host='localhost', port=6379)

def redis_cache(key_prefix, ttl=60):
    """
    Redis cache decorator
    :param key_prefix: Prefix for the key
    :param ttl: Time to live in seconds
    """
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            key = f'{key_prefix}:{args}:{kwargs}'
            result = cache.get(key)
            if result is not None:
                return result.decode('utf-8')
            result = function(*args, **kwargs)
            cache.set(key, str(result))
            cache.expire(key, time=ttl)
            return result
        return decorated_function
    return decorator