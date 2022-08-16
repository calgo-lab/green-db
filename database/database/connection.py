from datetime import datetime
from logging import getLogger
from typing import Iterator, List, Type

import pandas as pd
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

    def get_last_job_summary(self):
        """
        Fetch number of products in queried table with country, merchant and timestamp for the
        last time that the "start-job" ran.

        Yields:
            List[query]: `List` of domain object representations
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.country,
                self._database_class.merchant,
                self._database_class.timestamp,
            )
            timestamp = self.get_latest_timestamp()
            query = (
                db_session.query(*columns, func.count())
                .filter(self._database_class.timestamp == timestamp)
                .group_by(*columns)
                .all()
            )
            return query

    def get_all_last_job(self):
        """
        Fetch number of products in queried table with country, merchant and timestamp for all
        timestamps that "start-job" ran.

        Yields:
            List[query]: `List` of domain object representations
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.country,
                self._database_class.merchant,
                self._database_class.timestamp,
            )
            query = db_session.query(*columns, func.count()).group_by(*columns).all()
            return query


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

    def last_update_sustainability_labels(self) -> datetime:
        """
        Fetch all `SustainabilityLabel`s.

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

    def get_category_summary(self):
        """
        Fetch number of products per category per merchant from last timestamp found.

        Yields:
            DataFrame[query]: `DataFrame` of domain object representations
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.category, self._database_class.merchant)
            timestamp = self.get_latest_timestamp()
            query = (
                db_session.query(*columns, func.count())
                .filter(self._database_class.timestamp == timestamp)
                .group_by(*columns)
                .order_by(*columns)
                .all()
            )
            return pd.DataFrame(query, columns=["category", "merchant", "products"])

    def products_by_label(self):
        """
        Fetch number of products grouped by known and unknown sustainability labels for all
        timestamps.

        Yields:
            DataFrame[query]: `DataFrame` of domain object representations
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.timestamp,
                self._database_class.sustainability_labels,
            )
            query = db_session.query(*columns, func.count()).group_by(*columns).all()
            unknown = []
            known = []
            for row in query:
                for item in row:
                    if type(item) is list:
                        [
                            unknown.append(row)
                            if label == "certificate:UNKNOWN"
                            else known.append(row)
                            for label in item
                        ]

            unknown_df = pd.DataFrame(unknown, columns=["timestamp", "labels", "count"])
            unknown_df["date"] = pd.to_datetime(unknown_df["timestamp"]).dt.date
            unknown_cumm = unknown_df.groupby("date").sum()
            unknown_cumm["label"] = "certificate:UNKNOWN"
            known_df = pd.DataFrame(known, columns=["timestamp", "labels", "count"])
            known_df["date"] = pd.to_datetime(known_df["timestamp"]).dt.date
            known_cumm = known_df.groupby("date").sum()
            known_cumm["label"] = "Known certificates"
            join_df = pd.concat([unknown_cumm, known_cumm]).reset_index()
            return join_df
