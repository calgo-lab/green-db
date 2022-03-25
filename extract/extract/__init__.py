from typing import Optional

from core import log
from core.constants import TABLE_NAME_SCRAPING_OTTO, TABLE_NAME_SCRAPING_ZALANDO, \
    TABLE_NAME_SCRAPING_ASOS
from core.domain import Product, ScrapedPage

# Because we ignored the files `zalando.py` and `otto.py` we have to skip them here as well
from .extractors.asos import extract_asos  # type: ignore[attr-defined]
from .extractors.otto import extract_otto  # type: ignore[attr-defined]
from .extractors.zalando import extract_zalando  # type: ignore[attr-defined]
from .parse import parse_page, parse_json

log.setup_logger(__name__)

# Maps a scraping table name to its extraction method
EXTRACTOR_FOR_TABLE_NAME = {
    TABLE_NAME_SCRAPING_OTTO: extract_otto,
    TABLE_NAME_SCRAPING_ZALANDO: extract_zalando,
    TABLE_NAME_SCRAPING_ASOS: extract_asos,
}


def extract_product(table_name: str, scraped_page: ScrapedPage) -> Optional[Product]:
    """
    Extract product attributes and sustainability information from the `scraped_page`'s HTML.

    Args:
        table_name (str): Necessary to find the right extractor function
        scraped_page (ScrapedPage): Domain object representation of scraping table

    Returns:
        Optional[Product]: Returns a valid `Product` object or `None` if extraction failed
    """

    parsed_page = parse_page(scraped_page, is_json)
    return EXTRACTOR_FOR_TABLE_NAME[table_name](parsed_page)


def extract_product_json(table_name: str, scraped_page: ScrapedPage) -> Optional[Product]:
    """
    Extract product attributes and sustainability information from the `scraped_page`'s HTML.

    Args:
        table_name (str): Necessary to find the right extractor function
        scraped_page (ScrapedPage): Domain object representation of scraping table

    Returns:
        Optional[Product]: Returns a valid `Product` object or `None` if extraction failed
    """

    parsed_page = parse_json(scraped_page)
    return EXTRACTOR_FOR_TABLE_NAME[table_name](parsed_page)
