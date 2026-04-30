cache = {}

def get_cache(key):
    return cache.get(key)


def set_cache(key, value):
    cache[key] = value


def clear_cache(key):
    if key in cache:
        del cache[key]