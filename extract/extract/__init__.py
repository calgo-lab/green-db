from typing import Callable, Dict, Optional, Product

from core import log
from core.domain import ParsedPage, Product, ScrapedPage

from . import extractors
from .parse import parse_page

log.setup_logger(__name__)

# Maps a scraping table name to its extraction method
EXTRACTOR_FOR_TABLE_NAME: Dict[str, Callable[[ParsedPage], Optional[Product]]] = {}

for name in extractors.names:
    EXTRACTOR_FOR_TABLE_NAME |= getattr(extractors, name).EXTRACTOR_FOR_TABLE_NAME


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
