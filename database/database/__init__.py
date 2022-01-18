from logging import getLogger
from typing import Callable

from sqlalchemy.orm import Session

from core import log

from .domain import ScrapedPage, ScrapedPageGet

# TODO: Here decide which database to use
from .postgres import bootstrap_tables, get_session_factory
from .postgres.config import SCRAPING_DB_NAME
from .postgres.scraping import SCRAPING_DB_CLASS_FOR

log.setup_logger(__name__)
logger = getLogger(__name__)


class Scraping:
    def __init__(self, table: str):
        if table not in SCRAPING_DB_CLASS_FOR.keys():
            logger.error(f"Can't handle table: '{table}'")

        self.__table = table
        self.__database_class = SCRAPING_DB_CLASS_FOR[self.__table]
        self.__session_factory = get_session_factory(SCRAPING_DB_NAME)

        bootstrap_tables(SCRAPING_DB_NAME)

    def write_scraped_page(self, scraped_page: ScrapedPage) -> None:
        with self.__session_factory() as db_session:
            db_session.add(self.__database_class(**scraped_page.dict()))
            db_session.commit()

    def get_scraped_page(self, id: int) -> ScrapedPageGet:
        with self.__session_factory() as db_session:
            scraped_page = ScrapedPage.from_orm(
                db_session.query(self.__database_class)
                .filter(self.__database_class.id == id)
                .first()
            )

        return ScrapedPageGet(from_table=self.__table, **scraped_page.dict())
