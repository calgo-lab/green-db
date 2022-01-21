from typing import Optional

from core import log
from core.constants import TABLE_NAME_SCRAPING_OTTO, TABLE_NAME_SCRAPING_ZALANDO
from core.domain import Product, ScrapedPage

from .extractors.otto import extract_otto
from .extractors.zalando import extract_zalando
from .parse import parse_page

log.setup_logger(__name__)


EXTRACTOR_FOR_TABLE_NAME = {
    TABLE_NAME_SCRAPING_OTTO: extract_otto,
    TABLE_NAME_SCRAPING_ZALANDO: extract_zalando,
}


def extract_product(table_name: str, scraped_page: ScrapedPage) -> Optional[Product]:
    parsed_page = parse_page(scraped_page)
    return EXTRACTOR_FOR_TABLE_NAME[table_name](parsed_page)
