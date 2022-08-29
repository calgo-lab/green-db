from datetime import datetime
from logging import getLogger
from typing import Iterator, List, Type

from core.constants import DATABASE_NAME_GREEN_DB, DATABASE_NAME_SCRAPING
from core.domain import Product, ScrapedPage, SustainabilityLabel
from sqlalchemy import Column, func
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
        """
        Base `class` of connections.
        Makes sure the tables exists, offers `Session` factory and some basic methods.

        Args:
            database_class (Type[GreenDBTable] | Type[ScrapingTable]): Table class,
                necessary to write objects into database
            database_name (str): Name of the database,
                necessary for boostrapping and `Session` factory
        """
        self._database_class = database_class
        self._session_factory = get_session_factory(database_name)

        bootstrap_tables(database_name)

    # TODO: calling this one multiple times returns fewer and fewer examples...
    # TODO: Test and revise this!
    def _batching_query(
        self,
        db_query: Query,
        id_column: Column,
        DomainClass: Type[Product] | Type[ScrapedPage],
        batch_size: int = 1000,
    ) -> Iterator[Product | ScrapedPage]:
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
        """
        Writes a `domain_object` into the database and returns an updated Table object.
        This is useful if, e.g., the `id` of the database row is necessary in the future.

        Returns:
            [ScrapingTable | GreenDBTable]: Updated Table object representing the database row
        """
        with self._session_factory() as db_session:
            db_object = self._database_class(**domain_object.dict())
            db_session.add(db_object)
            db_session.commit()
            db_session.refresh(db_object)

        return db_object

    def __get_latest_timestamp(self, db_session: Session) -> datetime:
        """
        Helper method to fetch the latest available timestamp.

        Args:
            db_session (Session): `db_session` use for the query

        Returns:
            datetime: Latest timestamp available in database
        """
        return (
            db_session.query(self._database_class.timestamp)
            .distinct()
            .order_by(self._database_class.timestamp.desc())
            .first()
            .timestamp
        )

    def get_latest_timestamp(self) -> datetime:
        """
        Fetch the latest available timestamp.

        Returns:
            datetime: Latest timestamp available in database
        """
        with self._session_factory() as db_session:
            return self.__get_latest_timestamp(db_session)

    def is_timestamp_available(self, timestamp: datetime) -> bool:
        """
        Check whether the given `timestamp` is available in database.

        Args:
            timestamp (datetime): `timestamp` to check availability

        Returns:
            bool: Whether `timestamp` is available
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(self._database_class.timestamp)
                .filter(self._database_class.timestamp == timestamp)
                .first()
            )


class Scraping(Connection):
    def __init__(self, table_name: str):
        """
        `Connection` for scraping table defined by `table_name`.

        Args:
            table_name (str): Scraping `table_name` to connect to
        """
        if table_name not in SCRAPING_TABLE_CLASS_FOR.keys():
            error_message = f"Can't handle table: '{table_name}'"
            logger.error(error_message)
            raise ValueError(error_message)

        self.__table_name = table_name
        super().__init__(SCRAPING_TABLE_CLASS_FOR[self.__table_name], DATABASE_NAME_SCRAPING)

    def get_scraped_page(self, id: int) -> ScrapedPage:
        """
        Fetch `ScrapedPage` with given `id`.

        Args:
            id (int): Row `id` to fetch

        Returns:
            ScrapedPage: Domain object representation of table row
        """
        with self._session_factory() as db_session:
            return ScrapedPage.from_orm(
                db_session.query(self._database_class).filter(self._database_class.id == id).first()
            )

    def get_scraped_pages_for_timestamp(
        self, timestamp: datetime, batch_size: int = 1000
    ) -> Iterator[ScrapedPage]:
        """
        Fetch all `ScrapedPage`s for given `timestamp`.

        Args:
            timestamp (datetime): Defines which rows to fetch
            batch_size (int, optional): How many rows to fetch simultaneously. Defaults to 1000.

        Yields:
            Iterator[ScrapedPage]: Iterator over the domain object representations
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.timestamp == timestamp
            )
            return (ScrapedPage.from_orm(row) for row in query.all())

    def get_latest_scraped_pages(self, batch_size: int = 1000) -> Iterator[ScrapedPage]:
        """
        Fetch all `ScrapedPage`s for latest available `timestamp`.

        Args:
            batch_size (int, optional): How many rows to fetch simultaneously. Defaults to 1000.

        Yields:
            Iterator[ScrapedPage]: Iterator over the domain object representations
        """
        return self.get_scraped_pages_for_timestamp(
            self.get_latest_timestamp(), batch_size=batch_size
        )

    def get_scraping_summary(self) -> List[Query]:
        """
        Fetch number of products scraped in queried table by merchant and country for all
        timestamps found, excludes SERP page_type.

        Yields:
            List[query]: `List` of domain object representations
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.merchant,
                self._database_class.timestamp,
                self._database_class.country,
                self._database_class.page_type,
            )
            return (
                db_session.query(
                    self._database_class.merchant,
                    self._database_class.timestamp,
                    func.count(),
                    self._database_class.country,
                )
                .filter(self._database_class.page_type == "PRODUCT")
                .group_by(*columns)
                .all()
            )


class GreenDB(Connection):
    def __init__(self) -> None:
        """
        `Connection` for the GreenDB.
        Automatically pre-populates the sustainability labels table.
        """
        super().__init__(GreenDBTable, DATABASE_NAME_GREEN_DB)

        from core.sustainability_labels.bootstrap_database import sustainability_labels

        with self._session_factory() as db_session:
            # NOTE: this is slowly...
            # if we have many more labels to bootstrap, we should refactor it.
            if (  # If current label version (timestamp) does not exists, add them
                not db_session.query(SustainabilityLabelsTable.timestamp)
                .filter(SustainabilityLabelsTable.timestamp == sustainability_labels[0].timestamp)
                .first()
            ):

                for label in sustainability_labels:
                    db_session.add(SustainabilityLabelsTable(**label.dict()))

            db_session.commit()

    def get_product(self, id: int) -> Product:
        """
        Fetch `Product` with given `id`.

        Args:
            id (int): Row `id` to fetch

        Returns:
            Product: Domain object representation of table row
        """
        with self._session_factory() as db_session:
            return Product.from_orm(
                db_session.query(GreenDBTable).filter(GreenDBTable.id == id).first()
            )

    def get_sustainability_labels(
        self, iterator: bool = False
    ) -> List[SustainabilityLabel] | Iterator[SustainabilityLabel]:
        """
        Fetch all `SustainabilityLabel`s.

        Args:
            iterator (bool): Defines whether to return an `Iterator` or `list`

        Returns:
            List[SustainabilityLabel] | Iterator[SustainabilityLabel]: `list` or `Iterator
                of domain object representations
        """
        with self._session_factory() as db_session:

            sustainability_labels = db_session.query(SustainabilityLabelsTable).all()
            sustainability_labels_iterator = (
                SustainabilityLabel.from_orm(sustainability_label)
                for sustainability_label in sustainability_labels
            )
            if iterator:
                return sustainability_labels_iterator

            else:
                return list(sustainability_labels_iterator)

    def get_products_for_timestamp(
        self, timestamp: datetime, batch_size: int = 1000
    ) -> Iterator[Product]:
        """
        Fetch all `Product`s for given `timestamp`.

        Args:
            timestamp (datetime): Defines which rows to fetch
            batch_size (int, optional): How many rows to fetch simultaneously. Defaults to 1000.

        Yields:
            Iterator[Product]: `Iterator` of domain object representations
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.timestamp == timestamp
            )
            return (Product.from_orm(row) for row in query.all())

    def get_latest_products(self, batch_size: int = 1000) -> Iterator[Product]:
        """
        Fetch all `Product`s for latest available `timestamp`.

        Args:
            batch_size (int, optional): How many rows to fetch simultaneously. Defaults to 1000.

        Yields:
            Iterator[Product]: `Iterator` of domain object representation
        """
        return self.get_products_for_timestamp(self.get_latest_timestamp(), batch_size=batch_size)

    def get_extraction_summary(self) -> List[Query]:
        """
        Fetch number of products extracted by merchant and country for all timestamps found.

        Yields:
            List[Query]: Query result as `List`
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.merchant,
                self._database_class.timestamp,
                self._database_class.country,
            )
            return (
                db_session.query(
                    self._database_class.merchant,
                    self._database_class.timestamp,
                    func.count(),
                    self._database_class.country,
                )
                .group_by(*columns)
                .all()
            )

    def get_category_summary(self) -> List[Query]:
        """
        Fetch number of products in green_db tabler per category by merchant from last timestamp
        found.

        Yields:
            List[Query]: Query result as `List`
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.category, self._database_class.merchant)
            timestamp = self.get_latest_timestamp()
            return (
                db_session.query(*columns, func.count())
                .filter(self._database_class.timestamp == timestamp)
                .group_by(*columns)
                .order_by(*columns)
                .all()
            )

    def last_update_sustainability_labels(self) -> datetime:
        """
        Helper method to fetch the latest timestamp in sustainability_labels table

        Returns:
            datetime: Latest timestamp available in sustainability_labels table.
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(SustainabilityLabelsTable.timestamp)
                .distinct()
                .order_by(SustainabilityLabelsTable.timestamp.desc())
                .first()
                .timestamp
            )

    def products_by_sustainability_label(self) -> List[Query]:
        """
        Fetch number of products by sustainability label for all timestamps found.

        Yields:
            List[Query]: Query result as `List`
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.timestamp,
                self._database_class.sustainability_labels,  # type: ignore
            )
            return db_session.query(*columns, func.count()).group_by(*columns).all()

    def products_by_sustainability_label_timestamp(self, timestamp: datetime) -> List[Query]:
        """
        Fetch list of products given timestamp, including: id, name, url and
        sustainability labels for each product.

        Args:
            timestamp (datetime): Defines which rows to fetch

        Yields:
            List[Query]: Query result as `List`
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.id,
                self._database_class.timestamp,
                self._database_class.source,
                self._database_class.name,  # type: ignore
                self._database_class.url,
                self._database_class.sustainability_labels,  # type: ignore
            )
            return (
                db_session.query(*columns).filter(self._database_class.timestamp == timestamp).all()
            )
