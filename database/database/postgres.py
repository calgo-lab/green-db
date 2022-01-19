import os
from logging import getLogger
from typing import Callable, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import GREEN_DB_DB_NAME, SCRAPING_DB_NAME

logger = getLogger(__name__)


###############################
###### Scraping Settings ###### # noqa

SCRAPING_POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
SCRAPING_POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
SCRAPING_POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)
SCRAPING_POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)

SCRAPING_POSTGRES_URL = f"postgresql://{SCRAPING_POSTGRES_USER}:{SCRAPING_POSTGRES_PASSWORD}@{SCRAPING_POSTGRES_HOST}:{SCRAPING_POSTGRES_PORT}/{SCRAPING_DB_NAME}"  # noqa


##############################
###### GreenDB Settings ###### # noqa

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


BaseTable = declarative_base()


def __check_database(database: str) -> None:
    if database not in POSTGRES_URL_FOR.keys():
        logger.error(
            f"'database' not valid! Need to be one of: {', '.join(POSTGRES_URL_FOR.keys())}"
        )


def bootstrap_tables(database: str) -> None:
    __check_database(database)

    BaseTable.metadata.create_all(create_engine(POSTGRES_URL_FOR[database]))


def get_session_factory(database: str) -> Callable[[], Session]:
    __check_database(database)

    PostgresSession = sessionmaker(bind=create_engine(POSTGRES_URL_FOR[database]))

    def _get_postgres_session() -> Iterator[Session]:
        _get_postgres_session.session_number += 1

        session = PostgresSession()
        logger.debug(
            f"Created new postgres session #{_get_postgres_session.session_number} for database '{database}'."
        )

        try:
            yield session
        finally:
            session.close()
            logger.debug(
                f"Closed postgres session #{_get_postgres_session.session_number} for database '{database}'."
            )

    _get_postgres_session.session_number = 0

    return lambda: next(_get_postgres_session())
