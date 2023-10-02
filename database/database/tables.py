from datetime import datetime
from typing import Dict, List, Type

from sqlalchemy import (
    ARRAY,
    BIGINT,
    INTEGER,
    JSON,
    NUMERIC,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    Column,
    ForeignKey,
)

from core.constants import (
    TABLE_NAME_GREEN_DB,
    TABLE_NAME_PRODUCT_CLASSIFICATION,
    TABLE_NAME_PRODUCT_CLASSIFICATION_THRESHOLDS,
    TABLE_NAME_SCRAPING_AMAZON_DE,
    TABLE_NAME_SCRAPING_AMAZON_FR,
    TABLE_NAME_SCRAPING_AMAZON_GB,
    TABLE_NAME_SCRAPING_ASOS_FR,
    TABLE_NAME_SCRAPING_HM_FR,
    TABLE_NAME_SCRAPING_OTTO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_GB,
    TABLE_NAME_SUSTAINABILITY_LABELS,
)

# TODO: Here decide which database to use
from .postgres import (  # noqa
    GreenDBBaseTable,
    ScrapingBaseTable,
    bootstrap_tables,
    get_session_factory,
)


class __TableMixin:
    """
    Mixin `class` to add some convenience methods to table implementations.
    """

    @classmethod
    def get_columns(cls) -> List[str]:
        """
        Get the table's column names.

        Returns:
            List[str]: `list` of table's columns
        """
        return [a for a in cls.__dict__.keys() if not a.startswith("_")]

    def __repr__(self) -> str:
        """
        For convenience: `print` table object shows content.

        Returns:
            str: `str` representation of the table object.
        """
        columns = self.get_columns()

        def get_value_depending_on_type(column: str) -> str:
            value = getattr(self, column)
            if type(value) == str or type(value) == datetime:
                return f"'{value}'"
            else:
                return f"{value}"

        column_values_string = [
            f"{column}={get_value_depending_on_type(column)}"
            for column in columns
            if hasattr(self, column)
        ]
        return f"{self.__class__.__name__}({', '.join(column_values_string)})"


class ScrapingTable(__TableMixin):
    """
    Base `class` for Scraping tables that defined the columns.

    Args:
        __TableMixin ([type]): Mixin that implements some convenience methods
    """

    id = Column(INTEGER, nullable=False, autoincrement=True, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    source = Column(TEXT, nullable=False)
    merchant = Column(TEXT, nullable=False)
    country = Column(TEXT, nullable=False)
    category = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    html = Column(TEXT, nullable=False)
    page_type = Column(VARCHAR(length=10), nullable=False)
    gender = Column(TEXT, nullable=True)
    consumer_lifestage = Column(TEXT, nullable=True)
    meta_information = Column(JSON, nullable=True)


class ZalandoDeScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Zalando.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_ZALANDO_DE


class ZalandoFrScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Zalando.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_ZALANDO_FR


class ZalandoGbScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Zalando.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_ZALANDO_GB


class OttoDeScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Otto.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_OTTO_DE


class AsosFrScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Asos.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_ASOS_FR


class HmFrScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for H&M.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_HM_FR


class AmazonDeScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Amazon.
    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_AMAZON_DE


class AmazonFrScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Amazon France.
    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_AMAZON_FR


class AmazonGbScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Amazon United Kingdom.
    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_AMAZON_GB


# Used to dynamically map a table name to the correct Table class.
SCRAPING_TABLE_CLASS_FOR: Dict[str, Type[ScrapingTable]] = {
    TABLE_NAME_SCRAPING_ZALANDO_DE: ZalandoDeScrapingTable,
    TABLE_NAME_SCRAPING_ZALANDO_FR: ZalandoFrScrapingTable,
    TABLE_NAME_SCRAPING_ZALANDO_GB: ZalandoGbScrapingTable,
    TABLE_NAME_SCRAPING_OTTO_DE: OttoDeScrapingTable,
    TABLE_NAME_SCRAPING_ASOS_FR: AsosFrScrapingTable,
    TABLE_NAME_SCRAPING_AMAZON_DE: AmazonDeScrapingTable,
    TABLE_NAME_SCRAPING_AMAZON_FR: AmazonFrScrapingTable,
    TABLE_NAME_SCRAPING_AMAZON_GB: AmazonGbScrapingTable,
    TABLE_NAME_SCRAPING_HM_FR: HmFrScrapingTable,
}


class GreenDBTable(GreenDBBaseTable, __TableMixin):
    """
    Defines the GreenDB columns.

    Args:
        GreenDBBaseTable ([type]): `sqlalchemy` base class for the GreenDB database
        __TableMixin ([type]): Mixin that implements some convenience methods
    """

    __tablename__ = TABLE_NAME_GREEN_DB

    id = Column(INTEGER, nullable=False, autoincrement=True, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False)
    source = Column(TEXT, nullable=False)
    merchant = Column(TEXT, nullable=False)
    country = Column(TEXT, nullable=False)
    category = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    brand = Column(TEXT, nullable=False)
    sustainability_labels = Column(ARRAY(TEXT), nullable=False)  # TODO foreign keys to labels
    price = Column(NUMERIC, nullable=False)
    currency = Column(TEXT, nullable=False)
    image_urls = Column(ARRAY(TEXT), nullable=False)

    gender = Column(TEXT, nullable=True)
    consumer_lifestage = Column(TEXT, nullable=True)
    colors = Column(ARRAY(TEXT), nullable=True)
    sizes = Column(ARRAY(TEXT), nullable=True)

    gtin = Column(BIGINT, nullable=True)
    asin = Column(TEXT, nullable=True)


class SustainabilityLabelsTable(GreenDBBaseTable, __TableMixin):
    """
    Defines the SustainabilityLabels columns.

    Args:
        GreenDBBaseTable ([type]): `sqlalchemy` base class for the GreenDB database
        __TableMixin ([type]): Mixin that implements some convenience methods
    """

    __tablename__ = TABLE_NAME_SUSTAINABILITY_LABELS

    id = Column(TEXT, nullable=False, autoincrement=False, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False, primary_key=True)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    cred_credibility = Column(INTEGER, nullable=True)
    eco_chemicals = Column(INTEGER, nullable=True)
    eco_lifetime = Column(INTEGER, nullable=True)
    eco_water = Column(INTEGER, nullable=True)
    eco_inputs = Column(INTEGER, nullable=True)
    eco_quality = Column(INTEGER, nullable=True)
    eco_energy = Column(INTEGER, nullable=True)
    eco_waste_air = Column(INTEGER, nullable=True)
    eco_environmental_management = Column(INTEGER, nullable=True)
    social_labour_rights = Column(INTEGER, nullable=True)
    social_business_practice = Column(INTEGER, nullable=True)
    social_social_rights = Column(INTEGER, nullable=True)
    social_company_responsibility = Column(INTEGER, nullable=True)
    social_conflict_minerals = Column(INTEGER, nullable=True)


class ProductClassificationTable(GreenDBBaseTable, __TableMixin):
    """
    Defines the Product Classification columns.

    Args:
        GreenDBBaseTable ([type]): `sqlalchemy` base class for the GreenDB database
        __TableMixin ([type]): Mixin that implements some convenience methods
    """

    __tablename__ = TABLE_NAME_PRODUCT_CLASSIFICATION

    id = Column(
        INTEGER,
        ForeignKey(f"{TABLE_NAME_GREEN_DB}.id"),
        nullable=False,
        autoincrement=False,
        primary_key=True,
    )
    ml_model_name = Column(TEXT, nullable=False, primary_key=True)
    predicted_category = Column(TEXT, nullable=False)
    confidence = Column(NUMERIC, nullable=False)
    all_predicted_probabilities = Column(JSON, nullable=False)


class ProductClassificationThresholdsTable(GreenDBBaseTable, __TableMixin):
    """
    Defines the Product Classification Thresholds columns.

    Args:
        GreenDBBaseTable ([type]): `sqlalchemy` base class for the GreenDB database
        __TableMixin ([type]): Mixin that implements some convenience methods
    """

    __tablename__ = TABLE_NAME_PRODUCT_CLASSIFICATION_THRESHOLDS

    ml_model_name = Column(TEXT, nullable=False, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False, primary_key=True)
    source = Column(TEXT, nullable=False, primary_key=True)
    merchant = Column(TEXT, nullable=False, primary_key=True)
    predicted_category = Column(TEXT, nullable=False, primary_key=True)
    threshold = Column(NUMERIC, nullable=False)
