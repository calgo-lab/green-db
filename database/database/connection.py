from collections import Counter
from datetime import datetime
from logging import getLogger
from typing import Iterator, List, Optional, Type

import pandas as pd
from sqlalchemy import and_, case, desc, func, literal_column, cast, Integer
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
                    self._database_class.sustainability_labels.any(CertificateType.UNKNOWN.value)  # type: ignore[attr-defined] # noqa
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

    ### STARTS HERE ###
    ###################
    def get_sustainability_labels_credibility_notnull(self):
        """
        Subquery to get sustainability labels filtered by latest timestamp and not null values.
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(SustainabilityLabelsTable)
                .filter(
                    SustainabilityLabelsTable.cred_credibility != None,
                    SustainabilityLabelsTable.timestamp
                    == self.get_latest_timestamp(SustainabilityLabelsTable),
                )
                .subquery()
            )

    def get_unique_products_with_unnest_sustainability_labels(self):
        """
        Subquery to get all unique product ids with it's label, unnested in case product contains
        >1 label.
        """
        with self._session_factory() as db_session:
            return (
                db_session.query(
                    self._database_class.id.label("prod_id"),
                    # TO DO remove this and put it inside the join
                    self._database_class.merchant,
                    self._database_class.category,
                    self._database_class.brand,
                    func.unnest(self._database_class.sustainability_labels).label(
                        "sustainability_label"
                    ),
                )
                .distinct(self._database_class.url)
                .subquery()
            )

    # Functions using all unique products
    def get_product_count_credible_vs_not_credible_sustainability_labels(self, threshold: int = 50):
        """

        """
        with self._session_factory() as db_session:

            labels = self.get_sustainability_labels_credibility_notnull()

            all_unique = self.get_unique_products_with_unnest_sustainability_labels()

            unique_products_null_credibility = db_session.query(all_unique.c.merchant, func.count(
                all_unique.c.prod_id), literal_column("'credibility_null'")).filter(
                all_unique.c.sustainability_label.not_in(db_session.query(
                    labels.c.id).all())).group_by(all_unique.c.merchant).all()

            unique_credible_products = db_session.query(all_unique.c.merchant, func.count(
                all_unique.c.prod_id), literal_column("'credible'")).filter(
                all_unique.c.sustainability_label.in_(db_session.query(
                    labels.c.id).filter(labels.c.cred_credibility >= threshold).all())).group_by(
                all_unique.c.merchant).all()

            unique_not_credible_products = db_session.query(all_unique.c.merchant, func.count(
                all_unique.c.prod_id), literal_column("'not_credible'")).filter(
                all_unique.c.sustainability_label.in_(db_session.query(
                    labels.c.id).filter(labels.c.cred_credibility < threshold).all())).group_by(
                all_unique.c.merchant).all()

        return pd.DataFrame(unique_products_null_credibility + unique_credible_products +
                           unique_not_credible_products, columns=["merchant", "product_count",
                                                                  "type"])

    def get_rank_by_credibility(self, agregated_by: str, threshold: int = 50) -> pd.DataFrame:
        with self._session_factory() as db_session:
            # Filtering labels to make a 'lighter' join later on
            labels = self.get_sustainability_labels_credibility_notnull()

            # Query products for last timestamp
            all_unique = self.get_unique_products_with_unnest_sustainability_labels()

            # Join with labels tables to get credibility
            unique_with_credibility_not_null = (
                db_session.query(
                    all_unique.c.merchant,
                    all_unique.c.category,
                    all_unique.c.brand,
                    all_unique.c.sustainability_label,
                    labels.c.cred_credibility,
                )
                .join(
                    labels,
                    all_unique.c.sustainability_label == labels.c.id,
                    isouter=True,
                )
                .subquery()
            )
            # Filters
            if agregated_by == "merchant":
                aggregated_query = (
                    db_session.query(
                        unique_with_credibility_not_null.c.merchant,
                        func.round(
                            func.avg(unique_with_credibility_not_null.c.cred_credibility)
                        ).label("mean_credibility"),
                    )
                    .group_by(unique_with_credibility_not_null.c.merchant)
                    .order_by(desc("mean_credibility"))
                    .subquery()
                )
                return pd.DataFrame(
                    db_session.query(aggregated_query).all(),
                    columns=["merchant", "mean_credibility"],
                )

            elif agregated_by == "category":
                aggregated_query = (
                    db_session.query(
                        unique_with_credibility_not_null.c.category,
                        func.round(
                            func.avg(unique_with_credibility_not_null.c.cred_credibility)
                        ).label("mean_credibility"),
                    )
                    .group_by(unique_with_credibility_not_null.c.category)
                    .order_by(desc("mean_credibility"))
                    .subquery()
                )
                return pd.DataFrame(
                    db_session.query(aggregated_query)
                    .filter(aggregated_query.c.mean_credibility >= threshold)
                    .all(),
                    columns=["category", "mean_credibility"],
                )

            elif agregated_by == "brand":
                aggregated_query = (
                    db_session.query(
                        unique_with_credibility_not_null.c.brand,
                        func.round(
                            func.avg(unique_with_credibility_not_null.c.cred_credibility)
                        ).label("mean_credibility"),
                    )
                    .group_by(unique_with_credibility_not_null.c.brand)
                    .order_by(desc("mean_credibility"))
                    .subquery()
                )
                return pd.DataFrame(
                    db_session.query(aggregated_query)
                    .filter(aggregated_query.c.mean_credibility >= threshold)
                    .all(),
                    columns=["brand", "mean_credibility"],
                )

    # Functions only unique products with credibility
    def get_all_sustainability_scores_for_unique_products_with_credibility(
        self, threshold: int = 50
    ):
        """
        This function uses subquery 'get_unique_products_with_unnest_sustainability_labels' and then
            filters subquery 'self.get_sustainability_labels_credibility_notnull()' by credibility
            above threshold to finally calculate mean credibility and sustainability score.

            How sustainability score is computed? 1) Products with credibility below 50 are filtered;
            2) For products that have more than one sustainability label, max value is taken from
            each dimension; 3) Get mean of ecological(8) and social dimensions(5); 4) Calculate mean of
            ecological and social means.

            For products with more than one label, we take mean of credibility scores.

        Returns:
            A subquery with all unique product id's with credibility along it's mean_credibility,
            eco_mean_score, social_mean_score and sustainability_score.
        """
        with self._session_factory() as db_session:
            unique_all = self.get_unique_products_with_unnest_sustainability_labels()
            labels = self.get_sustainability_labels_credibility_notnull()
            credible_labels = (
                db_session.query(labels).filter(labels.c.cred_credibility >= threshold).subquery()
            )
            # Select max values for all ecological and social dimensions and mean credibility.
            get_max_scores = (
                db_session.query(
                    unique_all.c.prod_id,
                    case(
                        [
                            (
                                unique_all.c.category.in_(
                                    [
                                        "PRINTER",
                                        "LAPTOP",
                                        "TABLET",
                                        "DISHWASHER",
                                        "FRIDGE",
                                        "OVEN",
                                        "COOKER_HOOD",
                                        "FREEZER",
                                        "WASHER",
                                        "DRYER",
                                    ]
                                ),
                                literal_column("'electronics'"),
                            )
                        ],
                        else_=literal_column("'fashion'"),
                    ).label("product_family"),
                    func.max(credible_labels.c.eco_chemicals).label("eco_chemicals"),
                    func.max(credible_labels.c.eco_lifetime).label("eco_lifetime"),
                    func.max(credible_labels.c.eco_water).label("eco_water"),
                    func.max(credible_labels.c.eco_inputs).label("eco_inputs"),
                    func.max(credible_labels.c.eco_quality).label("eco_quality"),
                    func.max(credible_labels.c.eco_energy).label("eco_energy"),
                    func.max(credible_labels.c.eco_waste_air).label("eco_waste_air"),
                    func.max(credible_labels.c.eco_environmental_management).label(
                        "eco_environmental_management"
                    ),
                    func.max(credible_labels.c.social_labour_rights).label("social_labour_rights"),
                    func.max(credible_labels.c.social_business_practice).label(
                        "social_business_practice"
                    ),
                    func.max(credible_labels.c.social_social_rights).label("social_social_rights"),
                    func.max(credible_labels.c.social_company_responsibility).label(
                        "social_company_responsibility"
                    ),
                    func.max(credible_labels.c.social_conflict_minerals).label(
                        "social_conflict_minerals"
                    ),
                    func.round(func.avg(credible_labels.c.cred_credibility)).label(
                        "mean_credibility"
                    ),
                )
                .join(credible_labels, unique_all.c.sustainability_label == credible_labels.c.id)
                .group_by(unique_all.c.prod_id, unique_all.c.category)
                .subquery()
            )

            get_scores = (
                db_session.query(
                    get_max_scores.c.prod_id,
                    get_max_scores.c.product_family,
                    (
                        func.sum(
                            get_max_scores.c.eco_chemicals
                            + get_max_scores.c.eco_lifetime
                            + get_max_scores.c.eco_water
                            + get_max_scores.c.eco_inputs
                            + get_max_scores.c.eco_quality
                            + get_max_scores.c.eco_energy
                            + get_max_scores.c.eco_waste_air
                            + get_max_scores.c.eco_environmental_management
                        )
                        / 8
                    ).label("eco_mean_score"),
                    (
                        func.sum(
                            get_max_scores.c.social_labour_rights
                            + get_max_scores.c.social_business_practice
                            + get_max_scores.c.social_social_rights
                            + get_max_scores.c.social_company_responsibility
                            + get_max_scores.c.social_conflict_minerals
                        )
                        / 5
                    ).label("social_mean_score"),
                    get_max_scores.c.mean_credibility,
                )
                .group_by(
                    get_max_scores.c.prod_id,
                    get_max_scores.c.product_family,
                    get_max_scores.c.mean_credibility,
                )
                .subquery()
            )

            get_all_scores = (
                db_session.query(
                    get_scores.c.prod_id,
                    get_scores.c.product_family,
                    get_scores.c.mean_credibility,
                    get_scores.c.eco_mean_score,
                    get_scores.c.social_mean_score,
                    func.round(
                        (
                            func.sum(get_scores.c.eco_mean_score + get_scores.c.social_mean_score)
                            / 2
                        ),
                        0,
                    ).label("sustainability_score"),
                )
                .group_by(
                    get_scores.c.prod_id,
                    get_scores.c.product_family,
                    get_scores.c.mean_credibility,
                    get_scores.c.eco_mean_score,
                    get_scores.c.social_mean_score,
                )
                .subquery()
            )

            return get_all_scores

    def get_top_products_by_credibility_or_sustainability_score(
        self, merchants: list, categories: list, product_family_filter: str, top: int, rank_by: str
    ):
        """
        This function uses subquery 'get_sustainability_attributes_unique_products_with_credibility'
        to get unique products with credibility and it's scores to join it with the greendb table.
        """
        with self._session_factory() as db_session:
            get_product_scores = (
                self.get_all_sustainability_scores_for_unique_products_with_credibility()
            )
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
                    get_product_scores.c.product_family,
                    self._database_class.url,
                )
                .join(get_product_scores, self._database_class.id == get_product_scores.c.prod_id)
                .filter(
                    self._database_class.merchant.in_(merchants),
                    self._database_class.category.in_(categories),
                )
            )

            if product_family_filter != "all":
                query = query.filter(get_product_scores.c.product_family == product_family_filter)

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
                "family",
                "url",
            ],
        )

    def scores(self):
        with self._session_factory() as db_session:
            unnested = len(
                db_session.query(self.get_unique_products_with_unnest_sustainability_labels()).all()
            )

            unique_cred = len(
                db_session.query(
                    self.get_all_sustainability_scores_for_unique_products_with_credibility()
                ).all()
            )

            return unnested, unique_cred

    def get_product_count_by_label_and_category(self, threshold: int = 50):
        with self._session_factory() as db_session:
            unique_all = self.get_unique_products_with_unnest_sustainability_labels()
            labels = self.get_sustainability_labels_credibility_notnull()
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

    def get_scores_by_brand(self):
        with self._session_factory() as db_session:
            get_product_scores = (
                self.get_all_sustainability_scores_for_unique_products_with_credibility()
            )
            get_all_means = (
                db_session.query(
                    self._database_class.id,
                    self._database_class.brand,
                    self._database_class.category,
                    self._database_class.sustainability_labels,
                    get_product_scores.c.eco_mean_score,
                    get_product_scores.c.social_mean_score,
                    get_product_scores.c.mean_credibility,
                    get_product_scores.c.sustainability_score,
                    get_product_scores.c.product_family,
                )
                .join(
                    get_product_scores,
                    self._database_class.id == get_product_scores.c.prod_id,
                )
                .subquery()
            )
            return pd.DataFrame(
                db_session.query(
                    get_all_means.c.product_family,
                    get_all_means.c.category,
                    get_all_means.c.brand,
                    func.count(get_all_means.c.id),
                    func.round(func.avg(get_all_means.c.eco_mean_score), 2),
                    func.round(func.avg(get_all_means.c.social_mean_score), 2),
                    func.round(func.avg(get_all_means.c.sustainability_score), 2),
                    func.round(func.avg(get_all_means.c.mean_credibility), 2),
                )
                .group_by(
                    get_all_means.c.product_family,
                    get_all_means.c.category,
                    get_all_means.c.brand,
                )
                .all(),
                columns=[
                    "product_family",
                    "category",
                    "brand",
                    "product_count",
                    "eco_mean_score",
                    "social_mean_score",
                    "sustainability_score",
                    "mean_credibility",
                ],
            )
