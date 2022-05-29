from typing import Optional

from core.domain import Product

from ..parse import ParsedPage
from .amazon import extract_amazon


def extract_amazon_fr(parsed_page: ParsedPage) -> Optional[Product]:
    return extract_amazon(parsed_page=parsed_page)
