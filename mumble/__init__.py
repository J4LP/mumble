import requests_cache

requests_cache.install_cache('mumble_requests', backend='sqlite', expire_after=29)

__version__ = "0.0.1"

