import os

# TODO: Do not use the same user!
SCRAPING_POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
SCRAPING_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
SCRAPING_POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
SCRAPING_POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)

GREEN_DB_POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
GREEN_DB_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
GREEN_DB_POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
GREEN_DB_POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)
