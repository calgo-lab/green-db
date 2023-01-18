from typing import Optional

from core.domain import Product

from ..parse import ParsedPage
from .amazon_de import extract_amazon_de


def extract_amazon_gb(parsed_page: ParsedPage) -> Optional[Product]:
    return extract_amazon_de(parsed_page=parsed_page)
