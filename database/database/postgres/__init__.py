from logging import getLogger
from typing import Callable, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import POSTGRES_URL_FOR

logger = getLogger(__name__)


PostgresBaseClass = declarative_base()


def __check_database(database: str) -> None:
    if database not in POSTGRES_URL_FOR.keys():
        logger.error(
            f"'database' not valid! Need to be one of: {', '.join(POSTGRES_URL_FOR.keys())}"
        )


def bootstrap_tables(database: str) -> None:
    __check_database(database)

    PostgresBaseClass.metadata.create_all(create_engine(POSTGRES_URL_FOR[database]))


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
