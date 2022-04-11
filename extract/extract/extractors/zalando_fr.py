# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]

from logging import getLogger
from typing import Dict, Optional

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from .zalando import extract_zalando

logger = getLogger(__name__)


_LABEL_MAPPING = {
    "": CertificateType.OTHER,
    "Biodégradable": CertificateType.OTHER,
    "Biologique": CertificateType.OTHER,
    "bluesign®": CertificateType.OTHER,
    "Bronze Cradle to Cradle Certified®": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "Argent Cradle to Cradle Certified® ": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "Or Cradle to Cradle Certified® ": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Fabriqué avec 30-50% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec 50-70% de matériaux organiques": CertificateType.OTHER,
    "Fabriqué avec 50-70% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec 70-100% de matériaux organiques": CertificateType.OTHER,
    "Fabriqué avec 70-100% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec au moins 20 % d'alternatives biologiques innovantes aux combustibles fossiles": CertificateType.OTHER,  # noqa
    "Fabriqué avec au moins 20% d'alternatives innovantes au cuir": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de coton recyclé": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de matériaux innovants recyclés à partir de déchets": CertificateType.OTHER,  # noqa
    "Fabriqué avec au moins 50 % de polyuréthane à base d'eau": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de coton provenant de sources durables.": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de lyocell": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de matériaux responsables issus de forêts": CertificateType.OTHER,
    "Fabriqué avec de la laine provenant de sources responsables": CertificateType.OTHER,
    "Fabriqué avec du duvet provenant de sources responsables": CertificateType.OTHER,
    "Fairtrade Certified Cotton": CertificateType.FAIRTRADE_COTTON,
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "GOTS - made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "GOTS - organic": CertificateType.GOTS_ORGANIC,
    "Leather Working Group": CertificateType.LEATHER_WORKING_GROUP,
    "Moins d’emballage": CertificateType.OTHER,
    "Naturel": CertificateType.OTHER,
    "OCS - Organic Blended Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "OCS - Organic Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Respectueux des animaux": CertificateType.OTHER,
    "Respectueux des forêts": CertificateType.OTHER,
    "Responsible Down Standard": CertificateType.RESPONSIBLE_DOWN_STANDARD,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
}


def extract_zalando_fr(
    parsed_page: ParsedPage, label_mapping: Dict[str, CertificateType] = _LABEL_MAPPING
) -> Optional[Product]:
    return extract_zalando(parsed_page=parsed_page, label_mapping=label_mapping)
