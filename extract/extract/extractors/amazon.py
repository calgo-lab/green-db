import re
from logging import getLogger
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from core.sustainability_labels import load_and_get_sustainability_labels
from ..parse import ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def sustainability_label_to_certificate(labels) -> list[CertificateType]:
    sustainability_labels = load_and_get_sustainability_labels()

    result = {
        CertificateType[certificate.split(":")[-1]]
        for certificate, description in sustainability_labels.items()
        if any(_get_matchin_languages(description["languages"].values(), labels))
    }

    return result or {CertificateType.OTHER}


def _get_matchin_languages(languages, labels):
    return [
        language
        for language in languages
        if language["name"] in labels
    ]


def find_from_detail_table(soup, prop):
    product_details = soup.find("div", {"id": "detailBulletsWrapper_feature_div"})
    parent = product_details.find("span", text=re.compile(f"^{prop}")).parent
    return parent.findAll("span")[1].text


# TODO How to solve range of prices?
# TODO Is a currency mapping necessary?
def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text.strip()
    color = soup.find(
        "span", {"id": "inline-twister-expanded-dimension-text-color_name"}).text.strip()

    images = soup.find("div", {"id": "altImages"}).find_all("img")
    image_urls = [
        image["src"]
        for image in images
        if not image["src"].endswith(".gif")  # Filter out transparent gif
    ]

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = [span.text for span in sustainability_spans]
    sustainability_labels = sustainability_label_to_certificate(sustainability_texts)

    brand = find_from_detail_table(soup, "Manufacturer")
    asin = find_from_detail_table(soup, "ASIN")
    description = soup.find("div", {"id": "productDescription"}).p.get_text().strip()

    size = None
    price = 69.80
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
