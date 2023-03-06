from logging import getLogger
from typing import Optional

from core.domain import Product

from ..parse import ParsedPage
from .zalando_de import extract_zalando_de

logger = getLogger(__name__)


def extract_zalando_uk(parsed_page: ParsedPage) -> Optional[Product]:
    return extract_zalando_de(parsed_page=parsed_page)
