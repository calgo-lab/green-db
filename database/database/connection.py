from datetime import datetime
from logging import getLogger
from typing import Iterator, List, Type

from core.constants import DATABASE_NAME_GREEN_DB, DATABASE_NAME_SCRAPING
from core.domain import Product, ScrapedPage, SustainabilityLabel
from sqlalchemy import Column
from sqlalchemy.orm import Query, Session

from .tables import (
    SCRAPING_TABLE_CLASS_FOR,
    GreenDBTable,
    ScrapingTable,
    SustainabilityLabelsTable,
    bootstrap_tables,
    get_session_factory,
)

logger = getLogger(__name__)


class Connection:
    def __init__(
        self, database_class: Type[GreenDBTable] | Type[ScrapingTable], database_name: str
    ) -> None:
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
        TODO: PyDoc ..

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

    def write(self, domain_object: ScrapedPage | Product) -> ScrapingTable | GreenDBTable:
        with self._session_factory() as db_session:
            db_object = self._database_class(**domain_object.dict())
            db_session.add(db_object)
            db_session.commit()
            db_session.refresh(db_object)

        return db_object


class Scraping(Connection):
    def __init__(self, table_name: str):
        if table_name not in SCRAPING_TABLE_CLASS_FOR.keys():
            logger.error(f"Can't handle table: '{table_name}'")

        self.__table_name = table_name
        super().__init__(SCRAPING_TABLE_CLASS_FOR[self.__table_name], DATABASE_NAME_SCRAPING)

    def __get_latest_timestamp(self, db_session: Session) -> datetime:
        return (
            db_session.query(self._database_class.timestamp)
            .distinct()
            .order_by(self._database_class.timestamp.desc())
            .first()
            .timestamp
        )

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
                self._database_class.timestamp == timestamp
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
    def __init__(self) -> None:
        super().__init__(GreenDBTable, DATABASE_NAME_GREEN_DB)

        from .sustainability_labels import sustainability_labels

        with self._session_factory() as db_session:
            # NOTE: this is slowly..
            # if we have many more labels to bootstrap, we should refactor it.
            for label in sustainability_labels:
                if (  # If label does not exist
                    not db_session.query(SustainabilityLabelsTable.id)
                    .filter(SustainabilityLabelsTable.id == label.id)
                    .first()
                ):
                    db_session.add(SustainabilityLabelsTable(**label.dict()))

            db_session.commit()

    def get_product(self, id: int) -> Product:
        with self._session_factory() as db_session:
            return Product.from_orm(
                db_session.query(GreenDBTable).filter(GreenDBTable.id == id).first()
            )

    def get_sustainability_labels(self) -> List[SustainabilityLabel]:
        with self._session_factory() as db_session:
            return [
                SustainabilityLabel.from_orm(row)
                for row in db_session.query(SustainabilityLabelsTable).all()
            ]
