# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]

from logging import getLogger
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import JSON_LD, ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def extract_zalando_fr(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    if "/outfits/" in parsed_page.scraped_page.url:
        return None

    meta_data = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))

    name = meta_data.get("name", None)
    description = meta_data.get("description", None)
    brand = meta_data.get("brand", {}).get("name", None)
    color = meta_data.get("color", None)

    first_offer = safely_return_first_element(meta_data.get("offers", [{}]))
    currency = first_offer.get("priceCurrency", None)
    image_urls = meta_data.get("image", [])
    if price := first_offer.get("price", None):
        price = float(price)

    sustainability_labels = _get_sustainability(parsed_page.beautiful_soup)

    try:
        return Product(
            timestamp=parsed_page.scraped_page.timestamp,
            url=parsed_page.scraped_page.url,
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
# See: https://www.zalando.de/campaigns/about-sustainability/

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
    "Fabriqué avec au moins 20 % d'alternatives biologiques innovantes aux combustibles fossiles": CertificateType.OTHER,
    "Fabriqué avec au moins 20% d'alternatives innovantes au cuir": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de coton recyclé": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de matériaux innovants recyclés à partir de déchets": CertificateType.OTHER,
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


def _get_sustainability(beautiful_soup: BeautifulSoup) -> List[str]:
    """
    Extracts the sustainability information from HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML

    Returns:
        List[str]: Ordered `list` of found sustainability labels
    """

    if cluster := beautiful_soup.find("div", attrs={"data-testid": "cluster-certificates"}):
        labels = cluster.find_all(attrs={"data-testid": "certificate__title"})
        return sorted(
            {_LABEL_MAPPING.get(label.string, CertificateType.UNKNOWN) for label in labels}
        )
    return []
