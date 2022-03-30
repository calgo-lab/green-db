from datetime import datetime
from typing import Dict, List, Type

from sqlalchemy import ARRAY, BIGINT, INTEGER, JSON, NUMERIC, TEXT, TIMESTAMP, VARCHAR, Column

from core.constants import (
    TABLE_NAME_GREEN_DB,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
    TABLE_NAME_SCRAPING_AMAZON,
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
    merchant = Column(TEXT, nullable=False)
    category = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    html = Column(TEXT, nullable=False)
    page_type = Column(VARCHAR(length=10), nullable=False)
    meta_information = Column(JSON, nullable=True)


class ZalandoScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Zalando.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_ZALANDO


class OTTOScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Otto.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_OTTO


class AmazonScrapingTable(ScrapingBaseTable, ScrapingTable):
    """
    The actual scraping table for Amazon.

    Args:
        ScrapingBaseTable ([type]): `sqlalchemy` base class for the Scraping database
        ScrapingTable ([type]): To inherit the table definition
    """

    __tablename__ = TABLE_NAME_SCRAPING_AMAZON
    

# Used to dynamically map a table name to the correct Table class.
SCRAPING_TABLE_CLASS_FOR: Dict[str, Type[ScrapingTable]] = {
    TABLE_NAME_SCRAPING_ZALANDO: ZalandoScrapingTable,
    TABLE_NAME_SCRAPING_OTTO: OTTOScrapingTable,
    TABLE_NAME_SCRAPING_AMAZON: AmazonScrapingTable,
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
    merchant = Column(TEXT, nullable=False)
    category = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    brand = Column(TEXT, nullable=False)
    sustainability_labels = Column(ARRAY(TEXT), nullable=False)  # TODO foreign keys to labels
    price = Column(NUMERIC, nullable=False)
    currency = Column(TEXT, nullable=False)
    image_urls = Column(ARRAY(TEXT), nullable=False)

    color = Column(TEXT, nullable=True)
    size = Column(TEXT, nullable=True)

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
    timestamp = Column(TIMESTAMP, nullable=False)
    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    ecological_evaluation = Column(INTEGER, nullable=True)
    social_evaluation = Column(INTEGER, nullable=True)
    credibility_evaluation = Column(INTEGER, nullable=True)
