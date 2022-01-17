from datetime import datetime
from logging import getLogger
from typing import List

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import INTEGER, TEXT, TIMESTAMP, VARCHAR

from . import PostgresBaseClass
from .config import SCRAPING_DB_OTTO_TABLE_NAME, SCRAPING_DB_ZALANDO_TABLE_NAME

logger = getLogger(__name__)


class BaseScraping:
    id = Column(INTEGER, nullable=False, autoincrement=True, primary_key=True)
    start_timestamp = Column(TIMESTAMP, nullable=False)
    url = Column(TEXT, nullable=False)
    html = Column(TEXT, nullable=False)
    page_type = Column(VARCHAR(length=10), nullable=False)
    category = Column(VARCHAR(length=80), nullable=False)
    meta_information = Column(JSONB, nullable=True)

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


class ZalandoScraping(PostgresBaseClass, BaseScraping):
    __tablename__ = SCRAPING_DB_ZALANDO_TABLE_NAME


class OTTOScraping(PostgresBaseClass, BaseScraping):
    __tablename__ = SCRAPING_DB_OTTO_TABLE_NAME


SCRAPING_DB_CLASS_FOR = {
    SCRAPING_DB_ZALANDO_TABLE_NAME: ZalandoScraping,
    SCRAPING_DB_OTTO_TABLE_NAME: OTTOScraping,
}
