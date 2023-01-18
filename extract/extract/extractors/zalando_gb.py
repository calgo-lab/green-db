from logging import getLogger
from typing import Dict, Optional

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from .zalando_de import extract_zalando_de

logger = getLogger(__name__)


_LABEL_MAPPING = {
    "": CertificateType.OTHER,
    "bluesign® APPROVED materials": CertificateType.BLUESIGN_APPROVED,
    "Cradle to Cradle Certified ® Gold": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Cradle to Cradle Certified ® Silver": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "Fairtrade Certified Cotton": CertificateType.FAIRTRADE_COTTON,
    "Fairtrade Cotton": CertificateType.FAIRTRADE_COTTON,
    "Global Recycle Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Global Recycled Standard (GRS)": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "GOTS - made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "Global Organic Textile Standard (GOTS) - Organic": CertificateType.GOTS_ORGANIC,
    "Global Organic Textile Standard (GOTS) - Made with Organic": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,  # noqa
    "GOTS - organic": CertificateType.GOTS_ORGANIC,
    "Made with 30-50% recycled materials": CertificateType.OTHER,
    "Made with 50-70% organic materials": CertificateType.OTHER,
    "Made with 50-70% recycled materials": CertificateType.OTHER,
    "Made with 70-100% organic materials": CertificateType.OTHER,
    "Made with 70-100% recycled materials": CertificateType.OTHER,
    "Made with at least 20% innovative bio-based alternatives to fossil fuels": CertificateType.OTHER,  # noqa
    "Made with at least 20% innovative leather alternatives": CertificateType.OTHER,
    "Made with at least 20% innovative materials upcycled from waste": CertificateType.OTHER,
    "Made with at least 20% recycled cotton": CertificateType.OTHER,
    "Made with at least 50% lyocell": CertificateType.OTHER,
    "Made with at least 50% responsible forest-based materials": CertificateType.OTHER,
    "Made with at least 50% sustainably-sourced cotton": CertificateType.OTHER,
    "Made with at least 50% water-based polyurethane": CertificateType.OTHER,
    "Made with responsibly-sourced down": CertificateType.OTHER,
    "Made with responsibly-sourced wool": CertificateType.OTHER,
    "OCS - Organic Blended Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Organic Content Standard (OCS) - Blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "OCS - Organic Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard (OCS) - 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic": CertificateType.OTHER,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "Lyocell": CertificateType.OTHER,
    "Water-Based Polyurethane": CertificateType.OTHER,
}


def extract_zalando_uk(
    parsed_page: ParsedPage, label_mapping: Dict[str, CertificateType] = _LABEL_MAPPING
) -> Optional[Product]:
    return extract_zalando_de(parsed_page=parsed_page, label_mapping=label_mapping)
