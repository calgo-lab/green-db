from datetime import datetime
from logging import getLogger
from typing import Iterator, Optional, Type

from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy.orm import Query, Session

from .config import GREEN_DB_DB_NAME, SCRAPING_DB_NAME
from .domain import Product, ScrapedPage, ScrapedPageGet
from .tables import (
    SCRAPING_TABLE_CLASS_FOR,
    GreenDBTable,
    ScrapingTable,
    bootstrap_tables,
    get_session_factory,
)

logger = getLogger(__name__)


class Connection:
    def __init__(
        self, database_class: Type[GreenDBTable] | Type[ScrapingTable], database_name: str
    ):
        self._database_class = database_class
        self._session_factory = get_session_factory(database_name)

        bootstrap_tables(database_name)

    def _batching_query(
        self,
        query: Query,
        id_column: Column,
        return_class: Type[Product] | Type[ScrapedPage],
        batch_size: int = 1000,
    ) -> Iterator[BaseModel]:
        """
        Idea from here: https://github.com/sqlalchemy/sqlalchemy

        Args:
            query (Query): [description]
            id_column (Column): [description]
            return_class (Type[Product]): [description]
            batch_size (int, optional): [description]. Defaults to 1000.

        Yields:
            Iterator[BaseModel]: [description]
        """

        last_id = None

        while True:
            batched_query = query
            if last_id is not None:
                batched_query = batched_query.filter(id_column > last_id)
            chunk = batched_query.limit(batch_size).all()
            if not chunk:
                break
            last_id = chunk[-1].id
            for row in chunk:
                yield return_class.from_orm(row)


class Scraping(Connection):
    def __init__(self, table: str):
        if table not in SCRAPING_TABLE_CLASS_FOR.keys():
            logger.error(f"Can't handle table: '{table}'")

        self.__table = table
        super().__init__(SCRAPING_TABLE_CLASS_FOR[self.__table], SCRAPING_DB_NAME)

    def __get_latest_timestamp(self, db_session: Session) -> datetime:
        return (
            db_session.query(self._database_class.start_timestamp)
            .distinct()
            .order_by(self._database_class.start_timestamp.desc())
            .first()
            .start_timestamp
        )

    def write_scraped_page(self, scraped_page: ScrapedPage) -> ScrapingTable:
        with self._session_factory() as db_session:
            page = self._database_class(**scraped_page.dict())
            db_session.add(page)
            db_session.commit()
            db_session.refresh(page)

        return page

    def get_scraped_page(self, id: int) -> ScrapedPageGet:
        with self._session_factory() as db_session:
            scraped_page = ScrapedPage.from_orm(
                db_session.query(self._database_class).filter(self._database_class.id == id).first()
            )

        return ScrapedPageGet(from_table=self.__table, **scraped_page.dict())

    def get_latest_timestamp(self) -> datetime:
        with self._session_factory() as db_session:
            return self.__get_latest_timestamp(db_session)

    def get_scraped_pages_for_timestamp(
        self, timestamp: datetime, batch_size=1000
    ) -> Iterator[ScrapedPageGet]:
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.start_timestamp == timestamp
            )
            latest_scraped_pages = self._batching_query(
                query=query,
                id_column=self._database_class.id,
                return_class=ScrapedPage,
                batch_size=batch_size,
            )
            return (
                ScrapedPageGet(from_table=self.__table, **latest_scraped_page.dict())
                for latest_scraped_page in latest_scraped_pages
            )

    def get_latest_scraped_pages(self, batch_size=1000) -> Iterator[ScrapedPageGet]:
        return self.get_scraped_pages_for_timestamp(
            self.get_latest_timestamp(), batch_size=batch_size
        )


class GreenDB(Connection):
    def __init__(self):
        super().__init__(GreenDBTable, GREEN_DB_DB_NAME)

    def write_product(self, product: Product) -> GreenDBTable:
        with self._session_factory() as db_session:
            db_product = self._database_class(**product.dict())
            db_session.add(db_product)
            db_session.commit()
            db_session.refresh(db_product)

        return db_product

    def get_product(self, id: int) -> Product:
        with self._session_factory() as db_session:
            return Product.from_orm(
                db_session.query(self._database_class).filter(self._database_class.id == id).first()
            )
