from collections import Counter
from datetime import datetime
from logging import getLogger
from typing import Any, Iterator, List, Optional, Type

import pandas as pd
from sqlalchemy import desc, func, literal_column, or_
from sqlalchemy.orm import Session

from core.constants import (
    DATABASE_NAME_GREEN_DB,
    DATABASE_NAME_SCRAPING,
    PRODUCT_CLASSIFICATION_MODEL,
)
from core.domain import (
    CertificateType,
    PageType,
    Product,
    ProductClassification,
    ProductClassificationThreshold,
    ScrapedPage,
    SustainabilityLabel,
)

from .tables import (
    SCRAPING_TABLE_CLASS_FOR,
    GreenDBTable,
    ProductClassificationTable,
    ProductClassificationThresholdsTable,
    ScrapingTable,
    SustainabilityLabelsTable,
    bootstrap_tables,
    get_session_factory,
)

logger = getLogger(__name__)


class Connection:
    def __init__(
        self,
        database_class: Type[GreenDBTable] | Type[ScrapingTable] | Type[ProductClassificationTable],
        database_name: str,
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

    def write(
        self, domain_object: ScrapedPage | Product | ProductClassification
    ) -> ScrapingTable | GreenDBTable | ProductClassificationTable:
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
            Type[GreenDBTable]
            | Type[ScrapingTable]
            | Type[SustainabilityLabelsTable]
            | Type[ProductClassificationTable]
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
            Type[GreenDBTable]
            | Type[ScrapingTable]
            | Type[SustainabilityLabelsTable]
            | Type[ProductClassificationTable | ProductClassificationThresholdsTable]
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
            timestamp (datetime): Defines which rows to fetch.

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

    def get_scraped_page_count_per_merchant_and_country(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch count of scraped pages (excludes SERP `page_type`) for given `timestamp` or if `None`
            for all data.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.timestamp,
                self._database_class.merchant,
                self._database_class.country,
            )

            query = db_session.query(
                *columns,
                func.count(),
            ).filter(self._database_class.page_type == PageType.PRODUCT.value)

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).all()
            return pd.DataFrame(
                query, columns=["timestamp", "merchant", "country", "scraped_page_count"]
            ).convert_dtypes()  # use best possible dtypes

    def get_latest_scraped_page_count_per_merchant_and_country(self) -> pd.DataFrame:
        """
        Fetch count of scraped pages (excludes SERP `page_type`) for latest available timestamp.

        Returns:
           pd.DataFrame: Query results as `pd.DataFrame`.
        """
        return self.get_scraped_page_count_per_merchant_and_country(self.get_latest_timestamp())


class GreenDB(Connection):
    _database_class: Type[GreenDBTable]

    def __init__(self) -> None:
        """
        `Connection` for the GreenDB.
        Automatically pre-populates the sustainability labels table.
        """
        super().__init__(GreenDBTable, DATABASE_NAME_GREEN_DB)

        from core.product_classification_thresholds.bootstrap_database import thresholds
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

        #
        with self._session_factory() as db_session:
            # NOTE: this is slowly...
            # if we have many more thresholds to bootstrap, we should refactor it.
            if (  # If current threshold version (timestamp) does not exists, add them
                not db_session.query(
                    ProductClassificationThresholdsTable.timestamp,
                    ProductClassificationThresholdsTable.ml_model_name,
                )
                .filter(
                    ProductClassificationThresholdsTable.timestamp == thresholds[0].timestamp
                    and ProductClassificationThresholdsTable.ml_model_name
                    == thresholds[0].ml_model_name
                )
                .first()
            ):
                for threshold in thresholds:
                    db_session.add(ProductClassificationThresholdsTable(**threshold.dict()))

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
        self, timestamp: datetime, convert_orm: Optional[bool] = True
    ) -> Iterator[Product]:
        """
        Fetch all `Product`s for given `timestamp`.

        Args:
            convert_orm (boolean): Convert the results to Product instances or not.
            timestamp (datetime): Defines which rows to fetch

        Yields:
            Iterator[Product]: `Iterator` of domain object representations
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class)

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            if convert_orm:
                return (Product.from_orm(row) for row in query.all())
            else:
                return query.all()

    def get_latest_products(self, convert_orm: Optional[bool] = True) -> Iterator[Product]:
        """
        Fetch all `Product`s for latest available `timestamp`.

        Yields:
            Iterator[Product]: `Iterator` of domain object representation
        """
        return self.get_products_for_timestamp(self.get_latest_timestamp(), convert_orm)

    def get_product_count_per_merchant_and_country(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch product count by merchant and country for given timestamp, or if `None` for all data.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        with self._session_factory() as db_session:
            columns = (
                self._database_class.timestamp,
                self._database_class.merchant,
                self._database_class.country,
            )
            query = db_session.query(
                *columns,
                func.count(),
            )

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).order_by(self._database_class.timestamp.desc()).all()

            return pd.DataFrame(
                query, columns=["timestamp", "merchant", "country", "product_count"]
            ).convert_dtypes()  # use best possible dtypes

    def get_latest_product_count_per_merchant_and_country(self) -> pd.DataFrame:
        """
        Fetch product count per merchant and country for given timestamp for latest available
            timestamp.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        return self.get_product_count_per_merchant_and_country(self.get_latest_timestamp())

    def get_product_count_per_category_and_merchant(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch product count per category and merchant for given timestamp, or if `None` for all
            data.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.category, self._database_class.merchant)
            query = db_session.query(*columns, func.count())

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.group_by(*columns).all()

            return pd.DataFrame(
                query, columns=["category", "merchant", "product_count"]
            ).convert_dtypes()  # use best possible dtypes

    def get_latest_product_count_per_category_and_merchant(self) -> pd.DataFrame:
        """
        Fetch product count per category and merchant for latest available timestamp.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        return self.get_product_count_per_category_and_merchant(self.get_latest_timestamp())

    def get_product_count_per_sustainability_label(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch product count per sustainability_label by given timestamp or if `None` for all
            data. Products could have more than one sustainable label.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        with self._session_factory() as db_session:
            columns = (self._database_class.timestamp, self._database_class.sustainability_labels)
            query = db_session.query(*columns)
            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp).all()

            return pd.DataFrame.from_dict(
                (Counter([label for row in [q[1] for q in query] for label in row])),
                orient="index",
                columns=["product_count"],
            )

    def get_latest_product_count_per_sustainability_label(self) -> pd.DataFrame:
        """
        Fetch product count per sustainability label for latest available timestamp. Products could
            have more than one sustainable label.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        return self.get_product_count_per_sustainability_label(self.get_latest_timestamp())

    def get_product_count_with_unknown_sustainability_label(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch product count for products with `certificate:UNKNOWN` by given timestamp or if `None`
            for all data.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        with self._session_factory() as db_session:
            query = db_session.query(self._database_class.timestamp, func.count())

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = (
                query.filter(
                    self._database_class.sustainability_labels.any(CertificateType.UNKNOWN.value)
                    # type: ignore[attr-defined] # noqa
                )
                .group_by(self._database_class.timestamp)
                .all()
            )
            return pd.DataFrame(
                query, columns=["timestamp", "product_count"]
            ).convert_dtypes()  # use best possible dtypes

    def get_latest_product_count_with_unknown_sustainability_label(self) -> pd.DataFrame:
        """
        Fetch product count for products with `certificate:UNKNOWN` for latest available timestamp.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        return self.get_product_count_with_unknown_sustainability_label(self.get_latest_timestamp())

    def get_products_with_unknown_sustainability_label(
        self, timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch list of products with unknown sustainability label with: id, name, merchant and url
            per row by given timestamp or if `None` for all data.

        Args:
            timestamp (Optional[datetime], optional): Defines which rows to fetch. Defaults to None.

        Returns:
            pd.DataFrame: Query results as `pd.DataFrame`.
        """
        columns = (
            self._database_class.id,
            self._database_class.timestamp,
            self._database_class.source,
            self._database_class.name,
            self._database_class.url,
            self._database_class.sustainability_labels,
        )

        with self._session_factory() as db_session:
            query = db_session.query(*columns)

            if timestamp is not None:
                query = query.filter(self._database_class.timestamp == timestamp)

            query = query.filter(
                self._database_class.sustainability_labels.any(
                    CertificateType.UNKNOWN.value  # type: ignore[attr-defined]
                )
            ).all()

            return pd.DataFrame(
                query, columns=["id", "timestamp", "merchant", "name", "url", "labels"]
            ).convert_dtypes()  # use best possible dtypes

    def get_latest_products_with_unknown_sustainability_label(self) -> pd.DataFrame:
        """
        Fetch list of products with unknown sustainability label with: id, name, merchant and url
            per row for latest available timestamp.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        return self.get_products_with_unknown_sustainability_label(self.get_latest_timestamp())

    def get_sustainability_labels_subquery(self) -> Any:
        """
        Subquery to get sustainability labels filtered by latest timestamp and not null values.

        Returns:
            sqlalchemy.sql.selectable.Subquery
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(SustainabilityLabelsTable)
                .filter(
                    SustainabilityLabelsTable.timestamp
                    == self.get_latest_timestamp(SustainabilityLabelsTable),
                )
                .subquery()
            )

    def get_all_unique_products(self) -> Any:
        """
        Subquery to get all unique product together with merchant, category and sustainability
        labels.

        Returns:
            sqlalchemy.sql.selectable.Subquery
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(
                    self._database_class.id.label("prod_id"),
                    self._database_class.merchant,
                    self._database_class.category,
                    func.unnest(self._database_class.sustainability_labels).label(
                        "sustainability_label"
                    ),
                )
                .distinct(self._database_class.url)
                .subquery()
            )

    def get_product_count_by_sustainability_label_credibility(
        self, credibility_threshold: int = 50
    ) -> pd.DataFrame:
        """
        Function counts products by its sustainability labels credibility, >= 50 is credible,
            < 50 is not credible.

        Args:
            credibility_threshold (int): `credibility_threshold` to evaluate if sustainability
            label is credible or not. Default set as 50.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            labels = self.get_sustainability_labels_subquery()

            all_unique = self.get_all_unique_products()

            unique_credible_products = (
                db_session.query(
                    all_unique.c.merchant,
                    func.count(all_unique.c.prod_id),
                    literal_column("'credible'"),
                )
                .filter(
                    all_unique.c.sustainability_label.in_(
                        db_session.query(labels.c.id)
                        .filter(labels.c.cred_credibility >= credibility_threshold)
                        .all()
                    )
                )
                .group_by(all_unique.c.merchant)
                .all()
            )

            unique_not_credible_products = (
                db_session.query(
                    all_unique.c.merchant,
                    func.count(all_unique.c.prod_id),
                    literal_column("'not_credible'"),
                )
                .filter(
                    all_unique.c.sustainability_label.not_in(
                        db_session.query(labels.c.id)
                        .filter(labels.c.cred_credibility >= credibility_threshold)
                        .all()
                    )
                )
                .group_by(all_unique.c.merchant)
                .all()
            )

        return pd.DataFrame(
            unique_credible_products + unique_not_credible_products,
            columns=["merchant", "product_count", "type"],
        )

    def get_product_count_by_sustainability_label_credibility_all_timestamps(
        self, credibility_threshold: int = 50
    ) -> pd.DataFrame:
        """
        Function counts products by its sustainability labels credibility, >= 50 is credible,
            < 50 is not credible, Certificate:OTHER aka 3rd party labels and nulls by merchant.

        Args:
            credibility_threshold (int): `credibility_threshold` to evaluate if sustainability
            label is credible or not. Default set as 50.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            labels = self.get_sustainability_labels_subquery()

            credible_labels = [
                label[0]
                for label in db_session.query(labels.c.id)
                .filter(labels.c.cred_credibility >= credibility_threshold)
                .all()
            ]

            credible_products = (
                db_session.query(
                    self._database_class.timestamp,
                    self._database_class.merchant,
                    func.count(self._database_class.id),
                    literal_column("'credible'"),
                )
                .filter(
                    or_(
                        *[
                            self._database_class.sustainability_labels.any(label)
                            for label in credible_labels
                        ]
                    )
                )
                .group_by(
                    self._database_class.timestamp,
                    self._database_class.merchant,
                )
                .all()
            )

            not_credible_products = (
                db_session.query(
                    self._database_class.timestamp,
                    self._database_class.merchant,
                    func.count(self._database_class.id),
                    literal_column("'all_extracted'"),
                )
                .group_by(self._database_class.merchant, self._database_class.timestamp)
                .all()
            )

        products_certificate_other = (
            db_session.query(
                self._database_class.timestamp,
                self._database_class.merchant,
                func.count(self._database_class.id),
                literal_column("'certificate:OTHER'"),
            )
            .filter(
                self._database_class.sustainability_labels.any(CertificateType.OTHER.value)
            )  # type: ignore[attr-defined] # noqa
            .group_by(self._database_class.merchant, self._database_class.timestamp)
            .all()
        )

        return pd.DataFrame(
            credible_products + products_certificate_other + not_credible_products,
            columns=["timestamp", "merchant", "product_count", "type"],
        )

    def get_unique_products_with_credibility(self, credibility_threshold: int = 50) -> Any:
        """
        Subquery to return unique product id and its sustainability label(s) when they have at
        least one credible sustainability label.

        Args:
            credibility_threshold (int): `credibility_threshold` to evaluate if sustainability
            label is credible or not. Default set as 50.

        Returns:
            sqlalchemy.sql.selectable.Subquery

        """
        with self._session_factory() as db_session:
            labels = self.get_sustainability_labels_subquery()
            get_credible_labels = (
                db_session.query(labels.c.id)
                .filter(labels.c.cred_credibility >= credibility_threshold)
                .all()
            )
            credible_labels = [label[0] for label in get_credible_labels]

            return (
                db_session.query(
                    self._database_class.id.label("prod_id"),
                    self._database_class.sustainability_labels,
                )
                .distinct(self._database_class.url)
                .filter(
                    or_(
                        *[
                            self._database_class.sustainability_labels.any(label)
                            for label in credible_labels
                        ]
                    )
                )
                .subquery()
            )

    def calculate_sustainability_scores(self) -> Any:
        """
        This function gets unique product with credibility ids to calculate mean credibility,
        ecological, social and sustainability scores per id when products have at least one
        credible label.

        To calculate sustainability score:
        1) For products that have more than one sustainability label, max value is taken from
        eco and social each dimension and credibility is mean.
        2) All ecological (8) and social dimensions (5) are mean to get ecological and social
        scores
        3) Sustainability score is the mean of ecological and social scores

        Returns:
            A sqlalchemy.sql.selectable.Subquery with credibility, ecological, social and
            sustainability scores for unique credible products.
        """
        N_ECO_DIMENSIONS = 8
        N_SOC_DIMENSIONS = 5
        with self._session_factory() as db_session:
            all_unique_credible_products = self.get_unique_products_with_credibility()
            all_labels = self.get_sustainability_labels_subquery()
            unnested_labels = db_session.query(
                all_unique_credible_products.c.prod_id,
                func.unnest(all_unique_credible_products.c.sustainability_labels).label("label"),
            ).subquery()

            get_sustainability_attributes = (
                db_session.query(unnested_labels, all_labels)
                .join(all_labels, unnested_labels.c.label == all_labels.c.id)
                .subquery()
            )

            get_max_sustainability_scores = (
                db_session.query(
                    get_sustainability_attributes.c.prod_id,
                    func.max(get_sustainability_attributes.c.eco_chemicals).label("eco_chemicals"),
                    func.max(get_sustainability_attributes.c.eco_lifetime).label("eco_lifetime"),
                    func.max(get_sustainability_attributes.c.eco_water).label("eco_water"),
                    func.max(get_sustainability_attributes.c.eco_inputs).label("eco_inputs"),
                    func.max(get_sustainability_attributes.c.eco_quality).label("eco_quality"),
                    func.max(get_sustainability_attributes.c.eco_energy).label("eco_energy"),
                    func.max(get_sustainability_attributes.c.eco_waste_air).label("eco_waste_air"),
                    func.max(get_sustainability_attributes.c.eco_environmental_management).label(
                        "eco_environmental_management"
                    ),
                    func.max(get_sustainability_attributes.c.social_labour_rights).label(
                        "social_labour_rights"
                    ),
                    func.max(get_sustainability_attributes.c.social_business_practice).label(
                        "social_business_practice"
                    ),
                    func.max(get_sustainability_attributes.c.social_social_rights).label(
                        "social_social_rights"
                    ),
                    func.max(get_sustainability_attributes.c.social_company_responsibility).label(
                        "social_company_responsibility"
                    ),
                    func.max(get_sustainability_attributes.c.social_conflict_minerals).label(
                        "social_conflict_minerals"
                    ),
                    func.round(func.avg(get_sustainability_attributes.c.cred_credibility)).label(
                        "mean_credibility"
                    ),
                )
                .group_by(get_sustainability_attributes.c.prod_id)
                .subquery()
            )

            get_eco_and_social_means = (
                db_session.query(
                    get_max_sustainability_scores.c.prod_id,
                    (
                        func.sum(
                            get_max_sustainability_scores.c.eco_chemicals
                            + get_max_sustainability_scores.c.eco_lifetime
                            + get_max_sustainability_scores.c.eco_water
                            + get_max_sustainability_scores.c.eco_inputs
                            + get_max_sustainability_scores.c.eco_quality
                            + get_max_sustainability_scores.c.eco_energy
                            + get_max_sustainability_scores.c.eco_waste_air
                            + get_max_sustainability_scores.c.eco_environmental_management
                        )
                        / N_ECO_DIMENSIONS
                    ).label("ecological_score"),
                    (
                        func.sum(
                            get_max_sustainability_scores.c.social_labour_rights
                            + get_max_sustainability_scores.c.social_business_practice
                            + get_max_sustainability_scores.c.social_social_rights
                            + get_max_sustainability_scores.c.social_company_responsibility
                            + get_max_sustainability_scores.c.social_conflict_minerals
                        )
                        / N_SOC_DIMENSIONS
                    ).label("social_score"),
                    get_max_sustainability_scores.c.mean_credibility,
                )
                .group_by(
                    get_max_sustainability_scores.c.prod_id,
                    get_max_sustainability_scores.c.mean_credibility,
                )
                .subquery()
            )
            return (
                db_session.query(
                    get_eco_and_social_means.c.prod_id,
                    get_eco_and_social_means.c.mean_credibility,
                    get_eco_and_social_means.c.ecological_score,
                    get_eco_and_social_means.c.social_score,
                    func.round(
                        (
                            func.sum(
                                get_eco_and_social_means.c.ecological_score
                                + get_eco_and_social_means.c.social_score
                            )
                            / 2
                        ),
                        0,
                    ).label("sustainability_score"),
                )
                .group_by(
                    get_eco_and_social_means.c.prod_id,
                    get_eco_and_social_means.c.mean_credibility,
                    get_eco_and_social_means.c.ecological_score,
                    get_eco_and_social_means.c.social_score,
                )
                .subquery()
            )

    def get_rank_by_sustainability(self, aggregated_by: str) -> pd.DataFrame:
        """
        This function ranks unique credible products by its aggregated sustainability score.

        Args:
            aggregated_by (str): Determines product attribute to aggregated data.

        Returns:
            pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            unique_credible_products = self.calculate_sustainability_scores()

            aggregation_map = {
                "merchant": self._database_class.merchant,
                "category": self._database_class.category,
                "brand": self._database_class.brand,
            }

            return pd.DataFrame(
                db_session.query(
                    aggregation_map[aggregated_by],
                    func.round(func.avg(unique_credible_products.c.sustainability_score)).label(
                        "sustainability_score"
                    ),
                )
                .join(
                    unique_credible_products,
                    unique_credible_products.c.prod_id == self._database_class.id,
                )
                .group_by(aggregation_map[aggregated_by])
                .order_by(desc("sustainability_score"))
                .all(),
                columns=[f"{aggregated_by}", "sustainability_score"],
            )

    def get_top_products_by_credibility_or_sustainability_score(
        self, merchants: list, categories: list, top: int, rank_by: str
    ) -> pd.DataFrame:
        """
        This function gets unique credible products with its scores, adds products attributes:
            merchant, category, brand, name, url and sustainability labels to rank them by
            credibility or sustainability.

        Args:
            merchants (list) : Gets list of merchants to query.
            categories (list) : Gets list categories ro query.
            top (int): Gets number of products to fetch.
            rank_by: Determines y products will be order by its credibility or sustainability
            score.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            get_product_scores = self.calculate_sustainability_scores()
            query = (
                db_session.query(
                    self._database_class.id,
                    self._database_class.merchant,
                    self._database_class.category,
                    self._database_class.brand,
                    self._database_class.name,
                    self._database_class.sustainability_labels,
                    get_product_scores.c.mean_credibility,
                    get_product_scores.c.sustainability_score,
                    self._database_class.url,
                )
                .join(get_product_scores, self._database_class.id == get_product_scores.c.prod_id)
                .filter(
                    self._database_class.merchant.in_(merchants),
                    self._database_class.category.in_(categories),
                )
            )

            if rank_by == "credibility":
                ranked_products = query.order_by(desc(get_product_scores.c.mean_credibility)).limit(
                    top
                )
            elif rank_by == "sustainability_score":
                ranked_products = query.order_by(
                    desc(get_product_scores.c.sustainability_score)
                ).limit(top)

        return pd.DataFrame(
            ranked_products,
            columns=[
                "id",
                "merchant",
                "category",
                "brand",
                "name",
                "sustainability_labels",
                "CS",
                "SC",
                "url",
            ],
        )

    def get_product_count_by_sustainability_label_and_category(
        self, threshold: int = 50
    ) -> pd.DataFrame:
        """
        This functions gets product count by sustainability label and category for unique credible
        products.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            unique_all = self.get_all_unique_products()
            labels = self.get_sustainability_labels_subquery()
            credible_labels = (
                db_session.query(labels).filter(labels.c.cred_credibility >= threshold).subquery()
            )

            return pd.DataFrame(
                db_session.query(
                    func.count(unique_all.c.prod_id).label("product_count"),
                    unique_all.c.category,
                    credible_labels.c.name,
                )
                .join(credible_labels, unique_all.c.sustainability_label == credible_labels.c.id)
                .group_by(unique_all.c.category, credible_labels.c.name)
                .order_by(desc("product_count"))
                .all(),
                columns=["product_count", "category", "sustainability_label"],
            )

    def get_credibility_and_sustainability_scores_by_category(self) -> pd.DataFrame:
        """
        This function gets unique credible products ids and sustainability scores,
        adds brand, category and sustainability labels as product attributes and aggregates data
        at brand level.

        Returns:
           pd.DataFrame: Query results as `pd.Dataframe`.
        """
        with self._session_factory() as db_session:
            get_product_scores = self.calculate_sustainability_scores()
            get_all_means = (
                db_session.query(
                    self._database_class.id,
                    self._database_class.category,
                    get_product_scores.c.ecological_score,
                    get_product_scores.c.social_score,
                    get_product_scores.c.mean_credibility,
                    get_product_scores.c.sustainability_score,
                )
                .join(
                    get_product_scores,
                    self._database_class.id == get_product_scores.c.prod_id,
                )
                .subquery()
            )
            return pd.DataFrame(
                db_session.query(
                    get_all_means.c.category,
                    func.count(get_all_means.c.id),
                    func.round(func.avg(get_all_means.c.ecological_score), 2),
                    func.round(func.avg(get_all_means.c.social_score), 2),
                    func.round(func.avg(get_all_means.c.sustainability_score), 2),
                    func.round(func.avg(get_all_means.c.mean_credibility), 2),
                )
                .group_by(
                    get_all_means.c.category,
                )
                .all(),
                columns=[
                    "category",
                    "product_count",
                    "ecological_score",
                    "social_score",
                    "sustainability_score",
                    "mean_credibility",
                ],
            )

    def get_aggregated_unique_products(self) -> pd.DataFrame:
        """Fetches the unique rows ['url', 'id', 'categories', 'genders'].

        Aggregates the unique rows by ['url', 'timestamp'].

        :return:
            A pd.DataFrame of the fetched db rows.
        """
        with self._session_factory() as db_session:
            query = (
                db_session.query(
                    func.max(self._database_class.id),
                    func.max(self._database_class.url),
                    func.array_agg(self._database_class.category),
                    func.array_agg(self._database_class.gender),
                )
                .group_by(self._database_class.url, self._database_class.timestamp)
                .all()
            )
            columns = ["id", "url", "categories", "genders"]
            res_df = pd.DataFrame(query, columns=columns).convert_dtypes()
            return res_df.sort_values("id", ascending=False).drop_duplicates("url", keep="first")

    def get_products_with_ids(self, ids: list) -> Iterator[Product]:
        """Fetches the products for the given `ids`

        :param ids: A list of ids to filter the green-db::green-db rows.
        :return:
            An iterator of core.domain::Product.
        """
        with self._session_factory() as db_session:
            query = db_session.query(GreenDBTable).filter(GreenDBTable.id.in_(ids))
            return (Product.from_orm(row) for row in query.all())

    def get_product_classifications_with_ids(
        self, ids: list, ml_model_name: Optional[str] = PRODUCT_CLASSIFICATION_MODEL
    ) -> ProductClassification:
        """
        Fetch `Product's Classifications` for given `ids` and 'model name'.

        Args:
            ml_model_name: the name of the ml model used for prediction.
            ids (list): Row `ids` to fetch.

        Returns:
            Product: Domain object representation of table row
        """
        with self._session_factory() as db_session:
            query = db_session.query(ProductClassificationTable).filter(
                ProductClassificationTable.id.in_(ids)).filter(
                ProductClassificationTable.ml_model_name == ml_model_name)
            return (ProductClassification.from_orm(row) for row in query.all())

    def write_product_classification(self, product_classification: ProductClassification) -> None:
        """
        Writes a `ProductClassification domain_object` into the database.

        Args:
            product_classification: The domain object to write into the database.
        """
        with self._session_factory() as db_session:
            db_object = ProductClassificationTable(**product_classification.dict())
            db_session.add(db_object)
            db_session.commit()

    def write_product_classification_dataframe(self, data_frame: pd.DataFrame) -> None:
        """
        Writes a pd.Dataframe with multiple `ProductClassification domain_objects` into the
        database.

        Args:
            data_frame: a pd.Dataframe with multiple `ProductClassification domain_objects`
        """

        with self._session_factory() as db_session:
            df_len = len(data_frame)

            for index, (df_index, product_classification) in enumerate(
                data_frame.iterrows(), start=1
            ):
                try:
                    db_object = ProductClassificationTable(
                        **ProductClassification.parse_obj(product_classification).dict()
                    )
                    db_session.add(db_object)

                except Exception as e:
                    logger.info(f"error for product with index: {df_index}")
                    logger.info(f"{e}")

                # commit every 1000 products and at the end
                if (index % 1000 == 0) or (index == df_len):
                    db_session.commit()
                    logger.info(f"Committed {index} products")

    def get_product_classification_thresholds(
        self, timestamp: datetime, ml_model_name: str = PRODUCT_CLASSIFICATION_MODEL
    ) -> Iterator[ProductClassificationThreshold]:
        """
        Fetch `Product's Classification Thresholds` for given timestamp and ml_model_name.

        Args:
            timestamp: the timestamp when thresholds were calculated.
            ml_model_name: the name of the ml model for which the thresholds were calculated.

        Returns:
            Iterator[ProductClassificationThreshold]: `Iterator` of domain object representations.
        """

        with self._session_factory() as db_session:
            query = (
                db_session.query(ProductClassificationThresholdsTable)
                .filter(ProductClassificationThresholdsTable.timestamp == timestamp)
                .filter(ProductClassificationThresholdsTable.ml_model_name == ml_model_name)
            )
            return (ProductClassificationThreshold.from_orm(row) for row in query.all())

    def get_latest_product_classification_thresholds(
        self, ml_model_name: str = PRODUCT_CLASSIFICATION_MODEL
    ) -> Iterator[ProductClassificationThreshold]:
        """
        Fetch latest `Product's Classification Thresholds` for given ml_model_name.

        Args:
            ml_model_name: the name of the ml model for which the thresholds were calculated.

        Returns:
            Iterator[ProductClassificationThreshold]: `Iterator` of domain object representations
        """
        return self.get_product_classification_thresholds(
            self.get_latest_timestamp(ProductClassificationThresholdsTable), ml_model_name
        )
