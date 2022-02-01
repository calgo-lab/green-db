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
    """
    Checks whether `database_name` is defined. If not, logs an error.

    Args:
        database_name (str): Name of database to check
    """
    if database_name not in POSTGRES_URL_FOR.keys():
        logger.error(
            f"'database_name' not valid! Need to be one of: {', '.join(POSTGRES_URL_FOR.keys())}"
        )


def bootstrap_tables(database_name: str) -> None:
    """
    Creates all defined tables (if they do not exist) for the `database_name`.

    Args:
        database_name (str): Name of database to bootstrap
    """
    __check_database(database_name)

    POSTGRES_BASE_CLASS_FOR[database_name].metadata.create_all(
        create_engine(POSTGRES_URL_FOR[database_name])
    )


def get_session_factory(database_name: str) -> Callable[[], Session]:
    """
    Creates a `Session` factory for the `database_name`.
    When the `Session` factory is called it returns a `Session` and makes sure it will be closed.

    Args:
        database_name (str): Name of database to create a `Session` factory for

    Returns:
        Callable[[], Session]: `Session` factory for the `database_name`
    """
    __check_database(database_name)

    PostgresSession = sessionmaker(bind=create_engine(POSTGRES_URL_FOR[database_name]))

    def _get_postgres_session() -> Iterator[Session]:
        """
        Helper function that yields a `Session` and makes sure it will be closed.
        Additionally, it logs when a `Session` is created and closed. For this,
            we use function attributes.

        Yields:
            Iterator[Session]: Generator with exactly one `Session`
        """
        _get_postgres_session.session_number += 1  # type: ignore

        session = PostgresSession()
        logger.debug(
            f"Created new postgres session #{_get_postgres_session.session_number} "  # type: ignore
            f"for database '{database_name}'."
        )

        try:
            yield session
        finally:
            session.close()
            logger.debug(
                f"Closed postgres session #{_get_postgres_session.session_number} "  # type: ignore
                f"or database '{database_name}'."
            )

    _get_postgres_session.session_number = 0  # type: ignore

    return lambda: next(_get_postgres_session())
