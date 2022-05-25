from logging import getLogger
from typing import Dict, Optional

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from .amazon import extract_amazon

_LABEL_MAPPING = {}

def extract_amazon_fr(parsed_page: ParsedPage) -> Optional[Product]:
    return extract_amazon(parsed_page=parsed_page)