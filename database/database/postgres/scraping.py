from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import INTEGER, TEXT, TIMESTAMP, VARCHAR

from database.domain import ScrapedPage
from . import PostgresBaseClass
from .config import SCRAPING_DB_OTTO_TABLE_NAME, SCRAPING_DB_ZALANDO_TABLE_NAME


class __Scraping:
    id = Column(INTEGER, nullable=False, autoincrement=True, primary_key=True)
    start_timestamp = Column(TIMESTAMP, nullable=False)
    url = Column(TEXT, nullable=False)
    html = Column(TEXT, nullable=False)
    page_type = Column(VARCHAR(length=10), nullable=False)
    category = Column(VARCHAR(length=80), nullable=False)
    meta_information = Column(JSONB, nullable=True)


class ScrapingZalando(PostgresBaseClass, __Scraping):
    __tablename__ = SCRAPING_DB_ZALANDO_TABLE_NAME


class ScrapingOTTO(PostgresBaseClass, __Scraping):
    __tablename__ = SCRAPING_DB_OTTO_TABLE_NAME


# TODO Lesen schreiben zugriffe..
