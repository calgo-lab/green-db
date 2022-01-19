from datetime import datetime
from logging import getLogger
from typing import Iterator, Type

from sqlalchemy import Column
from sqlalchemy.orm import Query, Session

from .config import GREEN_DB_DB_NAME, SCRAPING_DB_NAME
from .domain import Product, ScrapedPage
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
        db_query: Query,
        id_column: Column,
        DomainClass: Type[Product] | Type[ScrapedPage],
        batch_size: int = 1000,
    ) -> Iterator[Product | ScrapedPage]:
        """
        Idea from here: https://github.com/sqlalchemy/sqlalchemy

        Args:
            db_query (Query): [description]
            id_column (Column): [description]
            DomainClass (Type[Product] | Type[ScrapedPage]): [description]
            batch_size (int, optional): [description]. Defaults to 1000.

        Yields:
            Iterator[Product | ScrapedPage]: [description]
        """

        last_id = None

        while True:
            batched_query = db_query
            if last_id is not None:
                batched_query = batched_query.filter(id_column > last_id)
            chunk = batched_query.limit(batch_size).all()
            if not chunk:
                break
            last_id = chunk[-1].id
            for row in chunk:
                yield DomainClass.from_orm(row)


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
            db_scraped_page = self._database_class(**scraped_page.dict())
            db_session.add(db_scraped_page)
            db_session.commit()
            db_session.refresh(db_scraped_page)

        return db_scraped_page

    def get_scraped_page(self, id: int) -> ScrapedPage:
        with self._session_factory() as db_session:
            return ScrapedPage.from_orm(
                db_session.query(self._database_class).filter(self._database_class.id == id).first()
            )

    def get_latest_timestamp(self) -> datetime:
        with self._session_factory() as db_session:
            return self.__get_latest_timestamp(db_session)

    def get_scraped_pages_for_timestamp(
        self, timestamp: datetime, batch_size: int = 1000
    ) -> Iterator[ScrapedPage]:
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.start_timestamp == timestamp
            )
            return self._batching_query(
                db_query=query,
                id_column=self._database_class.id,
                DomainClass=ScrapedPage,
                batch_size=batch_size,
            )

    def get_latest_scraped_pages(self, batch_size: int = 1000) -> Iterator[ScrapedPage]:
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
