import re
from logging import getLogger
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from core.sustainability_labels import load_and_get_sustainability_labels
from ..parse import ParsedPage


logger = getLogger(__name__)

def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text.strip()
    color = _get_color(soup)
    size = _get_sizes(soup)
    price = _get_price(soup)

    images = soup.find("div", {"id": "altImages"}).find_all("img")
    image_urls = [
        image["src"]
        for image in images
        if not image["src"].endswith(".gif")
           and "play-button-overlay" not in image["src"]
    ]

    currency = "EUR"

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = [span.text for span in sustainability_spans]
    sustainability_labels = sustainability_label_to_certificate(sustainability_texts)

    # TODO: Make sure german keys work for other categories
    brand = _find_from_details_section(soup, "Hersteller")
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
        sustainability_labels=sustainability_labels,
        price=price,
        currency=currency,
        image_urls=image_urls,
        color=color,
        size=size,
        gtin=None,
        asin=asin,
    )


# TODO: Are there more labels that need manual mapping?
def sustainability_label_to_certificate(labels) -> list[CertificateType]:
    sustainability_labels = load_and_get_sustainability_labels()
    manual_mapping = {
        "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    }

    result = {
        CertificateType[certificate.split(":")[-1]]
        for certificate, description in sustainability_labels.items()
        if any(_get_matching_languages(description["languages"].values(), labels))
    }

    for label in manual_mapping.keys():
        if label in labels:
            result.update({manual_mapping[label]})

    return result or {CertificateType.OTHER}


def _get_matching_languages(languages, labels):
    return [
        language
        for language in languages
        if language["name"] in labels
    ]


def _get_color(soup):
    color_intro = soup.find("span", {"class": "selection"})
    color_table = soup.find("tr", {"class": re.compile("po-color")})

    if color_intro:
        return color_intro.text.strip()

    if color_table:
        return color_table.find_all("span")[1].text


def _get_price(soup):
    price_range = soup.find("span", {"class": "a-price-range"})
    price_micro = soup.find("div", {"class":"a-section a-spacing-micro"})

    if price_range:
        prices = price_range.find_all("span", {"class": "a-offscreen"})
        price = float(((prices[0].text.replace(".", "")).replace("€", "")).replace(",", "."))  # Return the minimum price
        return price

    elif price_micro:
        s_price = price_micro.find("span", {"class": "a-offscreen"})
        price = float(((s_price.text.replace(".", "")).replace("€", "")).replace(",", "."))
        return price


# TODO: Are there more formats?
def _get_sizes(soup):
    sizes_other = soup.find_all("span", {"class", "a-size-base swatch-title-text-display swatch-title-text"})[1:]
    sizes_dropdown = soup.find_all("option", id=re.compile("size_name"))[1:]

    if sizes_other and sizes_other is not None:
        size = ", ".join([size.text.strip() for size in sizes_other])
        return size

    elif sizes_dropdown and sizes_other is not None:
        size = ", ".join([size.text.strip() for size in sizes_dropdown])
        return size


def _find_from_details_section(soup, prop):
    product_details_list = soup.find("div", {"id": "detailBulletsWrapper_feature_div"})
    product_details_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
    add_info_table = soup.find("table", {"id": "productDetails_detailBullets_sections1"})

    if product_details_list:
        parent = product_details_list.find("span", text=re.compile(f"^{prop}")).parent
        return parent.find_all("span")[1].text

    elif product_details_table:
        parent = product_details_table.find("th", text=re.compile(f"\s+{prop}\s+"))
        if parent is None:
            add_info_table = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
            parent = add_info_table.find("th", text=re.compile(f"{prop}")).parent
            return parent.find("td").text.strip()
        return parent.parent.find("td").text.strip().replace("\u200e", "")
