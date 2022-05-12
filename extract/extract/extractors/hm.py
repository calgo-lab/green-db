# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]
import json
from codecs import decode
from logging import getLogger
from typing import List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import JSON_LD, ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def extract_hm(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for www2.hm.com/fr_fr

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """

    if parsed_page.schema_org.get(JSON_LD):
        meta_data = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))
    else:
        meta_data = json.loads(parsed_page.beautiful_soup.find(id="product-schema").get_text())

    name = meta_data.get("name", None)
    description = meta_data.get("description", None)
    brand = meta_data.get("brand", {}).get("name", None)
    color = meta_data.get("color", None)

    first_offer = safely_return_first_element(meta_data.get("offers", [{}]))
    currency = first_offer.get("priceCurrency", None)
    image_urls = meta_data.get("image", [])
    # convert to list if its only one image
    if isinstance(image_urls, str):
        image_urls = [image_urls]
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
    # TM
    "Eastman Naia™": CertificateType.OTHER,
    "Viscose LivaEco™": CertificateType.OTHER,
    "Viscose LENZING™ ECOVERO™": CertificateType.OTHER,
    "Texloop™ RCOT™": CertificateType.OTHER,
    "REFIBRA™": CertificateType.OTHER,
    "Modal Tencel™": CertificateType.OTHER,
    "Lyocell Tencel™": CertificateType.OTHER,
    "Polyester recyclé REPREVE®": CertificateType.OTHER,
    "Our Ocean™": CertificateType.OTHER,
    "Nylon régénéré ECONYL®": CertificateType.OTHER,

    # recycle
    "Coton recyclé": CertificateType.OTHER,
    "Duvet recyclé": CertificateType.OTHER,
    "Laine recyclée": CertificateType.OTHER,
    "Laiton recyclé": CertificateType.OTHER,
    "PCTG recyclé": CertificateType.OTHER,
    "Papier recyclé": CertificateType.OTHER,
    "Plumes recyclé": CertificateType.OTHER,
    "Polystyrène recyclé": CertificateType.OTHER,
    "Polyamide recyclé": CertificateType.OTHER,
    "Polyester recyclé": CertificateType.OTHER,
    "zinc recyclé": CertificateType.OTHER,

    # other
    "In-conversion cotton": CertificateType.OTHER,
    "Lin biologique": CertificateType.OTHER,
    "Lyocell issue d’une gestion forestière durable": CertificateType.OTHER,
    "Coton biologique": CertificateType.OTHER,
    "Coton en conversion": CertificateType.OTHER,
}


def _get_sustainability(beautiful_soup: BeautifulSoup) -> List[str]:
    """
    Extracts the sustainability information from HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML

    Returns:
        List[str]: Ordered `list` of found sustainability labels
    """

    if materials := beautiful_soup.find("dt", text="Matériaux plus durables"):
        materials = materials.parent.find("dd").get_text().strip()
    elif materials := beautiful_soup.find("dt", text="Mat\\u00E9riaux plus durables'"):
        materials = decode(materials.next_sibling.get_text().strip(), "unicode-escape")
    else:
        return None  # the product does not contain sustainable information

    certificates = [
        certificate
        for (label, certificate) in _LABEL_MAPPING.items()
        if label.lower() in materials.lower()
    ]

    if certificates:
        return sorted(set(certificates))
    else:
        return [CertificateType.UNKNOWN]
