from core import log
from core.constants import (
    TABLE_NAME_SCRAPING_ASOS,
    TABLE_NAME_SCRAPING_OTTO,
    TABLE_NAME_SCRAPING_ZALANDO,
)
from database.connection import Scraping

log.setup_logger(__name__)

CONNECTION_FOR_TABLE = {
    TABLE_NAME_SCRAPING_ZALANDO: Scraping(TABLE_NAME_SCRAPING_ZALANDO),
    TABLE_NAME_SCRAPING_OTTO: Scraping(TABLE_NAME_SCRAPING_OTTO),
    TABLE_NAME_SCRAPING_ASOS: Scraping(TABLE_NAME_SCRAPING_ASOS),
}
