from importlib import import_module
from pathlib import Path
from pkgutil import walk_packages
from typing import Callable, Dict, Optional

from core import log
from core.domain import Product, ScrapedPage

from .parse import ParsedPage, parse_page

log.setup_logger(__name__)


EXTRACTORS_IMPLEMENTATION_PATH = "extractors"
EXTRACTOR_FOR_TABLE_NAME: Dict[str, Callable[[ParsedPage], Optional[Product]]] = {
    name: import_module(f"{__name__}.{EXTRACTORS_IMPLEMENTATION_PATH}.{name}").extract  # type: ignore # noqa
    for _, name, _ in walk_packages([str(Path(__file__).parent / EXTRACTORS_IMPLEMENTATION_PATH)])
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
