from datetime import datetime
from typing import Dict, List, Type

from sqlalchemy import ARRAY, INTEGER, JSON, NUMERIC, TEXT, TIMESTAMP, VARCHAR, Column

from core.constants import (
    TABLE_NAME_GREEN_DB,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
)

# TODO: Here decide which database to use
from .postgres import BaseTable, bootstrap_tables, get_session_factory


class __TableMixin:

    id = Column(INTEGER, nullable=False, autoincrement=True, primary_key=True)
    start_timestamp = Column(TIMESTAMP, nullable=False)
    merchant = Column(TEXT, nullable=False)
    category = Column(TEXT, nullable=False)
    url = Column(TEXT, nullable=False)

    @classmethod
    def get_columns(cls) -> List[str]:
        return [a for a in cls.__dict__.keys() if not a.startswith("_")]

    def __repr__(self):
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
    html = Column(TEXT, nullable=False)
    page_type = Column(VARCHAR(length=10), nullable=False)
    meta_information = Column(JSON, nullable=True)


class ZalandoScrapingTable(BaseTable, ScrapingTable):
    __tablename__ = TABLE_NAME_SCRAPING_ZALANDO


class OTTOScrapingTable(BaseTable, ScrapingTable):
    __tablename__ = TABLE_NAME_SCRAPING_OTTO


SCRAPING_TABLE_CLASS_FOR: Dict[str, Type[ScrapingTable]] = {
    TABLE_NAME_SCRAPING_ZALANDO: ZalandoScrapingTable,
    TABLE_NAME_SCRAPING_OTTO: OTTOScrapingTable,
}


class GreenDBTable(BaseTable, __TableMixin):
    __tablename__ = TABLE_NAME_GREEN_DB

    name = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    brand = Column(TEXT, nullable=False)
    sustainability_labels = Column(ARRAY(TEXT), nullable=False)
    price = Column(NUMERIC, nullable=False)
    currency = Column(TEXT, nullable=False)
    image_urls = Column(ARRAY(TEXT), nullable=False)

    color = Column(TEXT, nullable=True)
    size = Column(TEXT, nullable=True)

    gtin = Column(INTEGER, nullable=True)
    asin = Column(TEXT, nullable=True)
