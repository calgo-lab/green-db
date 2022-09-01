from datetime import datetime
from logging import getLogger
from typing import Iterator, List, Optional, Type

import pandas as pd
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from core.constants import DATABASE_NAME_GREEN_DB, DATABASE_NAME_SCRAPING
from core.domain import CertificateType, PageType, Product, ScrapedPage, SustainabilityLabel

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

    def __get_latest_timestamp(
        self,
        db_session: Session,
        database_class: Optional[
            Type[GreenDBTable] | Type[ScrapingTable] | Type[SustainabilityLabelsTable]
        ] = None,
    ) -> datetime:
        """
        Helper method to fetch the latest available timestamp.

        Args:
            db_session (Session): `db_session` use for the query
            database_class (
                Optional[Type[GreenDBTable] | Type[ScrapingTable] | Type[SustainabilityLabelsTable]]
            ): Optional database table to query. Defaults to None.

        Returns:
            datetime: Latest timestamp available in database
        """
        database_class = self._database_class if database_class is None else database_class

        return (
            db_session.query(database_class.timestamp)
            .distinct()
            .order_by(database_class.timestamp.desc())
            .first()
            .timestamp
        )

    def get_latest_timestamp(
        self,
        database_class: Optional[
            Type[GreenDBTable] | Type[ScrapingTable] | Type[SustainabilityLabelsTable]
        ] = None,
    ) -> datetime:
        """
        Fetch the latest available timestamp.

        Args:
            database_class (
                Optional[Type[GreenDBTable] | Type[ScrapingTable] | Type[SustainabilityLabelsTable]]
            ): Optional database table to query. Defaults to None.

        Returns:
            datetime: Latest timestamp available in database
        """
        with self._session_factory() as db_session:
            return self.__get_latest_timestamp(db_session, database_class=database_class)

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
    _database_class: Type[ScrapingTable]

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

    def get_scraped_pages_for_timestamp(self, timestamp: datetime) -> Iterator[ScrapedPage]:
        """
        Fetch all `ScrapedPage`s for given `timestamp`.

        Args:
            timestamp (datetime): Defines which rows to fetch

        Yields:
            Iterator[ScrapedPage]: Iterator over the domain object representations
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.timestamp == timestamp
            )
            return (ScrapedPage.from_orm(row) for row in query.all())

    def get_latest_scraped_pages(self) -> Iterator[ScrapedPage]:
        """
        Fetch all `ScrapedPage`s for latest available `timestamp`.

        Yields:
            Iterator[ScrapedPage]: Iterator over the domain object representations
        """
        return self.get_scraped_pages_for_timestamp(self.get_latest_timestamp())

    def get_scraping_summary(self, timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch number of products scraped in queried table by merchant and country given timestamp
            or if `None` for all data.
        Excludes SERP page_type.

        Args:
            timestamp (datetime): Defines which rows to fetch. Default as none to fetch all
            timestamps found.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.merchant,
                self._database_class.timestamp,
                self._database_class.country,
                self._database_class.page_type,
            )

            query = db_session.query(
                self._database_class.merchant,
                self._database_class.timestamp,
                func.count(),
                self._database_class.country,
            ).filter(self._database_class.page_type == PageType.PRODUCT.value)
            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).all()
            return query

    def get_latest_scraping_summary(self) -> pd.DataFrame:
        """
        Fetch number of products scraped in queried table by merchant and country for latest
        available timestamp.

        Returns:
           Dataframe: Query results as `Dataframe`.
        """
        return self.get_scraping_summary(self.get_latest_timestamp())


class GreenDB(Connection):
    _database_class: Type[GreenDBTable]

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

    def get_products_for_timestamp(self, timestamp: datetime) -> Iterator[Product]:
        """
        Fetch all `Product`s for given `timestamp`.

        Args:
            timestamp (datetime): Defines which rows to fetch

        Yields:
            Iterator[Product]: `Iterator` of domain object representations
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class).filter(
                self._database_class.timestamp == timestamp
            )
            return (Product.from_orm(row) for row in query.all())

    def get_latest_products(self) -> Iterator[Product]:
        """
        Fetch all `Product`s for latest available `timestamp`.

        Yields:
            Iterator[Product]: `Iterator` of domain object representation
        """
        return self.get_products_for_timestamp(self.get_latest_timestamp())

    def get_extraction_summary(self, timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch number of products extracted by merchant and country for given timestamp,
            or if `None` for all data.

        Args:
            timestamp (datetime): Defines which rows to fetch. Default as none to fetch all
            timestamps found.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.merchant,
                self._database_class.timestamp,
                self._database_class.country,
            )
            query = db_session.query(
                *columns,
                func.count(),
            )

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).order_by(self._database_class.timestamp.desc()).all()

            return pd.DataFrame(query, columns=["merchant", "timestamp", "country", "products"])

    def get_latest_extraction_summary(self) -> pd.DataFrame:
        """
        Fetch number of products extracted by merchant and country for latest available
        timestamp.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        return self.get_extraction_summary(self.get_latest_timestamp())

    def get_category_summary(self, timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch number of products in green_db table per category by merchant for given timestamp
            or if `None` for all data.

        Args:
            timestamp (datetime): Defines which rows to fetch. Default as none to fetch all
            timestamps found.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.category, self._database_class.merchant)
            query = db_session.query(*columns, func.count())
            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).order_by(*columns).all()

            return pd.DataFrame(query, columns=["category", "merchant", "products"])

    def get_latest_category_summary(self) -> pd.DataFrame:
        """
        Fetch number of products in green_db table per category by merchant for latest
        available timestamp.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        return self.get_category_summary(self.get_latest_timestamp())

    def get_products_by_label(self, timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch number of products in green_db table per sustainability_labels by given timestamp
            or if `None` for all data.

        Args:
            timestamp (datetime): Defines which rows to fetch. Default as none to fetch all
            timestamps found.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.timestamp, self._database_class.sustainability_labels)
            query = db_session.query(*columns, func.count())

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).all()
            return pd.DataFrame(query, columns=["timestamp", "labels", "count"])

    def get_latest_products_by_label(self) -> pd.DataFrame:
        """
        Fetch number of products in green_db table per sustainability_labels by latest available
        timestamp.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        return self.get_products_by_label(self.get_latest_timestamp())

    def get_labels_known_vs_unknown(self) -> pd.DataFrame:
        """
        Fetch number of products grouped by 'certificate:UNKNOWN' and all other certificates as
        'Known certificates' for all timestamps.

        Returns:
            DataFrame: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            unknown = (
                db_session.query(self._database_class.timestamp, func.count())
                .filter(
                    self._database_class.sustainability_labels.any(CertificateType.UNKNOWN.value)  # type: ignore[attr-defined] # noqa
                )
                .group_by(self._database_class.timestamp)
                .all()
            )
            unknown_df = pd.DataFrame(unknown, columns=["timestamp", "count"])
            unknown_df["label"] = CertificateType.UNKNOWN.value  # type: ignore[attr-defined]
            known = (
                db_session.query(self._database_class.timestamp, func.count())
                .filter(
                    ~self._database_class.sustainability_labels.any(CertificateType.UNKNOWN.value)  # type: ignore[attr-defined] # noqa
                )
                .group_by(self._database_class.timestamp)
                .all()
            )
            known_df = pd.DataFrame(known, columns=["timestamp", "count"])
            known_df["label"] = "Known certificates"
            return pd.concat([unknown_df, known_df])

    def get_latest_products_certificate_unknown(self) -> pd.DataFrame:
        """
        Fetch list of products with 'certificate:UNKNOWN' for latest available timestamp,
        including: id, name, url and sustainability labels.

        Returns:
            Dataframe: Query results as `Dataframe`.
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.id,
                self._database_class.timestamp,
                self._database_class.source,
                self._database_class.name,
                self._database_class.url,
                self._database_class.sustainability_labels,
            )
            query = (
                db_session.query(*columns)
                .filter(
                    and_(
                        self._database_class.timestamp == self.get_latest_timestamp(),
                        self._database_class.sustainability_labels.any(
                            CertificateType.UNKNOWN.value  # type: ignore[attr-defined]
                        ),
                    )
                )
                .all()
            )
            return pd.DataFrame(
                query, columns=["id", "timestamp", "merchant", "name", "url", "labels"]
            )
