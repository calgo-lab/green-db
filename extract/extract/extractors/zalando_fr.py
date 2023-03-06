from logging import getLogger
from typing import Dict, Optional

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from .zalando_de import extract_zalando_de

logger = getLogger(__name__)


def extract_zalando_fr(parsed_page: ParsedPage) -> Optional[Product]:
    return extract_zalando_de(parsed_page=parsed_page)
