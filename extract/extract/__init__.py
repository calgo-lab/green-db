from typing import Dict, Optional

from core import log
from core.domain import Product, ScrapedPage

from . import extractors
from .parse import parse_page
from .utils import ExtractorMapping, ExtractorSignature

log.setup_logger(__name__)

# Maps a scraping table name to its extraction method
EXTRACTOR_FOR_TABLE_NAME: Dict[str, ExtractorSignature] = {}

for module_name in extractors.names:
    module = getattr(extractors, module_name)
    for member_name in dir(module):
        member = getattr(module, member_name)
        if isinstance(member, ExtractorMapping):
            EXTRACTOR_FOR_TABLE_NAME |= member.map


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
