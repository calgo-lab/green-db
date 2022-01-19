import os

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_USER = os.environ.get("REDIS_USER", None)
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
