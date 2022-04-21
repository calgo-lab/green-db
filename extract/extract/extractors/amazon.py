import re
from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from core.sustainability_labels import load_and_get_sustainability_labels
from ..parse import ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def sustainability_label_to_certificate(label) -> CertificateType:
    for cert, desc in load_and_get_sustainability_labels().items():
        for language in desc["languages"].keys():
            if desc["languages"][language]["name"] == label:
                return cert
    return CertificateType.OTHER


# TODO Review cases with more than one certificate
# TODO How to solve range of prices?
# TODO Is a currency mapping necessary?
def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text
    color = soup.find("span", {"id": "inline-twister-expanded-dimension-text-color_name"}).text.strip()

    images = soup.find("div", {"id": "altImages"}).find_all("img")
    image_urls = [
        image["src"]
        for image in images
        if not image["src"].endswith(".gif") # Filter out transparent gif
    ]

    sustainability_labels_text = soup.find("span", id=re.compile("CPF-BTF-Certificate-Name")).text
    sustainability_labels = sustainability_label_to_certificate(sustainability_labels_text)

    description = ""
    brand = ""
    asin = ""
    size = ""
    price = None
    currency = "EUR"

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
        size=size,
        gtin=None,
        asin=asin,
    )
