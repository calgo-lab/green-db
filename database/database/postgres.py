from logging import getLogger
from typing import Callable, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from core.constants import DATABASE_NAME_GREEN_DB, DATABASE_NAME_SCRAPING
from core.postgres import (
    GREEN_DB_POSTGRES_HOST,
    GREEN_DB_POSTGRES_PASSWORD,
    GREEN_DB_POSTGRES_PORT,
    GREEN_DB_POSTGRES_USER,
    SCRAPING_POSTGRES_HOST,
    SCRAPING_POSTGRES_PASSWORD,
    SCRAPING_POSTGRES_PORT,
    SCRAPING_POSTGRES_USER,
)

logger = getLogger(__name__)


ScrapingBaseTable = declarative_base()
GreenDBBaseTable = declarative_base()

SCRAPING_POSTGRES_URL = f"postgresql://{SCRAPING_POSTGRES_USER}:{SCRAPING_POSTGRES_PASSWORD}@{SCRAPING_POSTGRES_HOST}:{SCRAPING_POSTGRES_PORT}/{DATABASE_NAME_SCRAPING}"  # noqa
GREEN_DB_POSTGRES_URL = f"postgresql://{GREEN_DB_POSTGRES_USER}:{GREEN_DB_POSTGRES_PASSWORD}@{GREEN_DB_POSTGRES_HOST}:{GREEN_DB_POSTGRES_PORT}/{DATABASE_NAME_GREEN_DB}"  # noqa

POSTGRES_URL_FOR = {
    DATABASE_NAME_SCRAPING: SCRAPING_POSTGRES_URL,
    DATABASE_NAME_GREEN_DB: GREEN_DB_POSTGRES_URL,
}

POSTGRES_BASE_CLASS_FOR = {
    DATABASE_NAME_SCRAPING: ScrapingBaseTable,
    DATABASE_NAME_GREEN_DB: GreenDBBaseTable,
}


def __check_database(database_name: str) -> None:
    if database_name not in POSTGRES_URL_FOR.keys():
        logger.error(
            f"'database_name' not valid! Need to be one of: {', '.join(POSTGRES_URL_FOR.keys())}"
        )


def bootstrap_tables(database_name: str) -> None:
    __check_database(database_name)

    POSTGRES_BASE_CLASS_FOR[database_name].metadata.create_all(
        create_engine(POSTGRES_URL_FOR[database_name])
    )


def get_session_factory(database_name: str) -> Callable[[], Session]:
    __check_database(database_name)

    PostgresSession = sessionmaker(bind=create_engine(POSTGRES_URL_FOR[database_name]))

    def _get_postgres_session() -> Iterator[Session]:
        _get_postgres_session.session_number += 1

        session = PostgresSession()
        logger.debug(
            f"Created new postgres session #{_get_postgres_session.session_number} for database '{database_name}'."
        )

        try:
            yield session
        finally:
            session.close()
            logger.debug(
                f"Closed postgres session #{_get_postgres_session.session_number} for database '{database_name}'."
            )

    _get_postgres_session.session_number = 0

    return lambda: next(_get_postgres_session())
