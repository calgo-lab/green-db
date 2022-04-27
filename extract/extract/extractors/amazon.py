import re
from logging import getLogger
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from core.sustainability_labels import load_and_get_sustainability_labels
from ..parse import MICRODATA, ParsedPage

logger = getLogger(__name__)

def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text.strip()
    color = soup.find("span", {"id": "inline-twister-expanded-dimension-text-color_name"}).text.strip()

    sizes = soup.find_all("span", {"class", "a-size-base swatch-title-text-display swatch-title-text"})[1:]
    size = ", ".join([size.text.strip() for size in sizes])

    images = soup.find("div", {"id": "altImages"}).find_all("img")
    image_urls = [
        image["src"]
        for image in images
        if not image["src"].endswith(".gif")
        and "play-button-overlay" not in image["src"]
    ]

    currency = "EUR"
    price_range = soup.find("span", {"class": "a-price-range"})
    prices = price_range.find_all("span", {"class": "a-offscreen"})
    price = float(prices[-1].text[1:])  # Return the maximum price

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = [span.text for span in sustainability_spans]
    sustainability_labels = sustainability_label_to_certificate(sustainability_texts)

    brand = _find_from_details_section(soup, "Manufacturer")
    asin = _find_from_details_section(soup, "ASIN")
    description = soup.find("div", {"id": "productDescription"}).p.get_text().strip()

    return Product(
        timestamp=parsed_page.scraped_page.timestamp,
        url=parsed_page.scraped_page.url,
        merchant=parsed_page.scraped_page.merchant,
        category=parsed_page.scraped_page.category,
        name=name,
        description=description,
        brand=brand,
        sustainability_labels=sustainability_texts,
        price=price,
        currency=currency,
        image_urls=image_urls,
        color=color,
        size=size,
        gtin=None,
        asin=asin,
    )

def sustainability_label_to_certificate(labels) -> list[CertificateType]:
    sustainability_labels = load_and_get_sustainability_labels()

    result = {
        CertificateType[certificate.split(":")[-1]]
        for certificate, description in sustainability_labels.items()
        if any(_get_matching_languages(description["languages"].values(), labels))
    }

    # TODO: Are there more labels that need manual mapping?
    if "Global Recycled Standard" in labels:
        result.update({CertificateType.GLOBAL_RECYCLED_STANDARD})

    return result or {CertificateType.OTHER}


def _get_matching_languages(languages, labels):
    return [
        language
        for language in languages
        if language["name"] in labels
    ]


def _find_from_details_section(soup, prop):
    product_details_list = soup.find("div", {"id": "detailBulletsWrapper_feature_div"})
    product_details_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})

    if product_details_list:
        parent = product_details_list.find("span", text=re.compile(f"^{prop}")).parent
        return parent.find_all("span")[1].text
    elif product_details_table:
        parent = product_details_table.find("th", text=re.compile(f"\s+{prop}\s+")).parent
        return parent.find("td").text.strip().replace("\u200e", "")