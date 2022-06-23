# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]
import json
import re
from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from ..utils import safely_return_first_element, safely_convert_attribute_to_array

logger = getLogger(__name__)


def extract_asos_fr(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from html, which in this case is a json
    and returns `Product` object or `None` if anything failed. Works for asos.com.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """

    page_json = json.loads(parsed_page.scraped_page.html)

    name = page_json.get("name", None)
    description = format_description(page_json.get("description", None))
    brand = page_json.get("brand", {}).get("name", None)
    first_offer = safely_return_first_element(page_json.get("variants", [{}]))

    colors = safely_convert_attribute_to_array(first_offer.get("colour", None))
    currency = first_offer.get("price", {}).get("currency", None)

    images = page_json.get("media", {}).get("images", {})
    image_urls = [image.get("url", "") for image in images]

    if price := first_offer.get("price", {}).get("current", {}).get("value", None):
        price = float(price)

    sizes = [variant.get("displaySizeText", None) for variant in page_json.get("variants", [])]

    url = _get_url(page_json.get("localisedData", []), "fr-FR")
    sustainability_labels = _get_sustainability(page_json.get("info", {}).get("aboutMe", ""))

    try:
        return Product(
            timestamp=parsed_page.scraped_page.timestamp,
            url=url,
            source=parsed_page.scraped_page.source,
            merchant=parsed_page.scraped_page.merchant,
            country=parsed_page.scraped_page.country,
            category=parsed_page.scraped_page.category,
            gender=parsed_page.scraped_page.gender,
            consumer_lifestage=parsed_page.scraped_page.consumer_lifestage,
            name=name,
            description=description,
            brand=brand,
            sustainability_labels=sustainability_labels,
            price=price,
            currency=currency,
            image_urls=image_urls,
            colors=colors,
            sizes=sizes,
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
    "au moins 40 % de matières recyclées": CertificateType.OTHER,
}


def _get_url(localized_data: List[Dict[str, str]], lang: str) -> str:
    """
    Extracts the language specific url from the List.

    Args:
        localized_data (List): List of dictionaries consisting of language, title and url
        beautiful_soup (BeautifulSoup): Parsed HTML

    Returns:
        str: language specific url
    """

    for country in localized_data:
        if country.get("locale", "") == lang:
            return country.get("pdpUrl", "")
    return ""


def format_description(html: str):
    """
    Helper function to convert description including html tags to a string.

    Args:
        html (str): string with html tags

    Returns:
        cleaned string without html tags. HTML 'li' tags are replaced with '. '
    """

    clean_regex = re.compile("<(?!((li)|(/li))).*?>")  # exclude all tags except 'li' tags
    clean_string = re.sub(clean_regex, "", html)
    soup = BeautifulSoup(clean_string, "html.parser")
    return soup.get_text(". ", strip=True)  # get text and replace all 'li' tags with '. '


def _get_sustainability(about_me: str) -> List[str]:
    """
    Extracts the sustainability information from HTML.

    Args:
        about_me (str): string including the sustainability information if available

    Returns:
        List[str]: Ordered `list` of found sustainability labels
    """

    certificates = [
        certificate
        for (label, certificate) in _LABEL_MAPPING.items()
        if label.lower() in about_me.lower()
    ]

    if certificates:
        return sorted(set(certificates))
    else:
        return []
