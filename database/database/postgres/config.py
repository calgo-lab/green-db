import os

###############################
###### Scraping Settings ###### # noqa

SCRAPING_DB_NAME = "scraping"
SCRAPING_DB_ZALANDO_TABLE_NAME = "zalando"
SCRAPING_DB_OTTO_TABLE_NAME = "otto"

SCRAPING_POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
SCRAPING_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
SCRAPING_POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
SCRAPING_POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)

SCRAPING_POSTGRES_URL = f"postgresql://{SCRAPING_POSTGRES_USER}:{SCRAPING_POSTGRES_PASSWORD}@{SCRAPING_POSTGRES_HOST}:{SCRAPING_POSTGRES_PORT}/{SCRAPING_DB_NAME}"  # noqa


##############################
###### GreenDB Settings ###### # noqa

GREEN_DB_DB_NAME = "green-db"
GREEN_DB_TABLE_NAME = "green-db"

GREEN_DB_POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
GREEN_DB_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
GREEN_DB_POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
GREEN_DB_POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)

GREEN_DB_POSTGRES_URL = f"postgresql://{GREEN_DB_POSTGRES_USER}:{GREEN_DB_POSTGRES_PASSWORD}@{GREEN_DB_POSTGRES_HOST}:{GREEN_DB_POSTGRES_PORT}/{GREEN_DB_DB_NAME}"  # noqa


##########################
###### Dependencies ###### # noqa
POSTGRES_URL_FOR = {
    SCRAPING_DB_NAME: SCRAPING_POSTGRES_URL,
    GREEN_DB_DB_NAME: GREEN_DB_POSTGRES_URL,
}
