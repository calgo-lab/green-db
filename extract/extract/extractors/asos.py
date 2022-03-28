# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]
import json
from logging import getLogger
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from ..utils import remove_html_tags, safely_return_first_element

logger = getLogger(__name__)


def extract_asos(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for zalando.de.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """

    page_json = json.loads(parsed_page.scraped_page.html)

    name = page_json.get("name", None)
    # description = remove_html_tags(page_json.get("description", None))
    description = remove_html_tags(page_json.get("info", {}).get("aboutMe", ""))
    brand = page_json.get("brand", {}).get("name", None)
    first_offer = safely_return_first_element(page_json.get("variants", [{}]))
    color = first_offer.get("colour", None)
    currency = first_offer.get("price", {}).get("currency", None)

    images = page_json.get("media", {}).get("images", {})
    image_urls = [image.get("url", "") for image in images]

    if price := first_offer.get("price", {}).get("current", {}).get("value", None):
        price = float(price)

    url = _get_url(page_json.get("localisedData", []), "fr-FR")
    sustainability_labels = _get_sustainability(
        remove_html_tags(page_json.get("info", {}).get("aboutMe", "")))

    try:
        return Product(
            timestamp=parsed_page.scraped_page.timestamp,
            url=url,
            merchant=parsed_page.scraped_page.merchant,
            category=parsed_page.scraped_page.category,
            name=name,
            description=description,
            brand=brand,
            sustainability_labels=sustainability_labels,
            price=price,
            currency=currency,
            image_urls=image_urls,
            color=color,
            size=None,
            gtin=None,
            asin=None,
        )

    except ValidationError as error:
        # TODO Handle Me!!
        # error contains relatively nice report why data ist not valid
        logger.info(error)
        return None


# TODO: How can we do this smart?
# See: https://www.asos.com/responsible-fashion/partner/our-certification-partners/
_LABEL_MAPPING = {
    "Better Cotton Initiative": CertificateType.BETTER_COTTON_INITIATIVE,
    "Better Coton Initiative": CertificateType.BETTER_COTTON_INITIATIVE,
    "Cotton made in Africa": CertificateType.COTTON_MADE_IN_AFRICA,
    "Modal TENCEL™": CertificateType.OTHER,
    "Lyocell Tencel™": CertificateType.OTHER,
    "TENCEL™ Lyocell": CertificateType.OTHER,
    "LENZING™ ECOVERO™": CertificateType.OTHER,
    "Viscose Ecovero™": CertificateType.OTHER,
    "coton bio": CertificateType.OTHER,
    "Zinc recyclé": CertificateType.OTHER,
    "polyester recyclé": CertificateType.OTHER,
    "plastique recyclé": CertificateType.OTHER,
    "Argent massif recyclé": CertificateType.OTHER,
    "laine recyclée": CertificateType.OTHER,
    "laiton recyclé": CertificateType.OTHER,
    "au moins 50 % de matières recyclées": CertificateType.OTHER,
    "coton recyclé": CertificateType.OTHER,
    "polyamide recyclé": CertificateType.OTHER,
    "nylon recyclé": CertificateType.OTHER,
    "fils recyclés": CertificateType.OTHER,
    "matériaux recyclés": CertificateType.OTHER,
    "acier recyclé": CertificateType.OTHER,
    "lastiques recyclés": CertificateType.OTHER,
    "En polyuréthane à base d'eau Meilleur pour l'environnement, car le processus génère moins de pollution": CertificateType.OTHER,  # noqa
    "Fabriqué en utilisant moins d'eau et en produisant moins de déchets": CertificateType.OTHER,
    "Sa confection demande moins d'eau et produit moins de déchets": CertificateType.OTHER,
    "fabriqué en polyuréthane à base d'eau": CertificateType.OTHER,
    "Ce jean a nécessité 50 % d'eau en moins au cours du lavage": CertificateType.OTHER,
    "au moins 40 % de matières recyclées": CertificateType.OTHER

    # Following labels are listed on the above link,
    # but the corresponding string has not yet been identified

    # "": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    # "": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    # "": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED
    # "": CertificateType.LEATHER_WORKING_GROUP,
    # "": CertificateType.RESPONSIBLE_DOWN_STANDARD,
    # "": CertificateType.GLOBAL_RECYCLED_STANDARD,
    # "": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    # "": CertificateType.RECYCLED_CLAIM_STANDARD_100,
}


def _get_url(localized_data: List, lang: str) -> str:
    for country in localized_data:
        if country.get("locale", "") == lang:
            return country.get("pdpUrl", "")
    return ""


def _get_sustainability(about_me: str) -> List[str]:
    """
    Extracts the sustainability information from HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML

    Returns:
        List[str]: Ordered `list` of found sustainability labels
    """

    certificates = [certificate for (label, certificate) in _LABEL_MAPPING.items()
                    if label.lower() in about_me.lower()]

    if certificates:
        return sorted(set(certificates))
    else:
        return [CertificateType.UNKNOWN]
