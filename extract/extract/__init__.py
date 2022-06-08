from typing import Optional

from core import log
from core.constants import (
    TABLE_NAME_SCRAPING_AMAZON_DE,
    TABLE_NAME_SCRAPING_ASOS_FR,
    TABLE_NAME_SCRAPING_OTTO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_DE,
    TABLE_NAME_SCRAPING_ZALANDO_FR,
    TABLE_NAME_SCRAPING_ZALANDO_UK,
)
from core.domain import Product, ScrapedPage

from .extractors.amazon import extract_amazon_de  # type: ignore[attr-defined]

# Because we ignored the files `zalando.py` and `otto.py` we have to skip them here as well
from .extractors.asos import extract_asos_fr  # type: ignore[attr-defined]
from .extractors.otto import extract_otto_de  # type: ignore[attr-defined]
from .extractors.zalando import extract_zalando_de  # type: ignore[attr-defined]
from .extractors.zalando_fr import extract_zalando_fr  # type: ignore[attr-defined]
from .extractors.zalando_gb import extract_zalando_uk  # type: ignore[attr-defined]
from .parse import parse_page

log.setup_logger(__name__)

# Maps a scraping table name to its extraction method
EXTRACTOR_FOR_TABLE_NAME = {
    TABLE_NAME_SCRAPING_AMAZON_DE: extract_amazon_de,
    TABLE_NAME_SCRAPING_ASOS_FR: extract_asos_fr,
    TABLE_NAME_SCRAPING_OTTO_DE: extract_otto_de,
    TABLE_NAME_SCRAPING_ZALANDO_DE: extract_zalando_de,
    TABLE_NAME_SCRAPING_ZALANDO_FR: extract_zalando_fr,
    TABLE_NAME_SCRAPING_ZALANDO_UK: extract_zalando_uk,
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

    parsed_page = parse_page(scraped_page)
    return EXTRACTOR_FOR_TABLE_NAME[table_name](parsed_page)
