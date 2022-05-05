import re
import json
from logging import getLogger
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product
from core.sustainability_labels import load_and_get_sustainability_labels
from ..utils import safely_return_first_element
from ..parse import ParsedPage


logger = getLogger(__name__)

def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text.strip()
    color = _get_color(soup)
    size = _get_sizes(soup)
    price = float(parsed_page.scraped_page.meta_information['price'].replace(",", "."))

    images = soup.find("div", {"id": "altImages"}).find_all("img")
    image_urls = [
        image["src"]
        for image in images
        if not image["src"].endswith(".gif")
           and "play-button-overlay" not in image["src"]
           and "play-icon-overlay" not in image["src"]
           and "360_icon" not in image["src"]
    ]

    currency = "EUR"

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = [span.text for span in sustainability_spans]
    sustainability_labels = sustainability_label_to_certificate(sustainability_texts)

    brand = _get_brand(soup)
    description = _get_description(soup)
    asin = _find_from_details_section(soup, "ASIN")

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


class DocumentExtractor():
    def __init__(self, targets: list) -> None:
        self.targets = targets

    def __call__(self, extraction) -> Optional[str]:
        if any(self.targets):
            result = [target for target in self.targets if target][0]
            return extraction(result)


def _get_color(soup):
    targets = [
        soup.find("span", {"class": "selection"}),
        soup.find("tr", {"class": re.compile("po-color")}),
    ]

    def parse_color(element):
        from_table = getattr(element.find_all("span")[1], "text", None)
        from_intro = element.text.strip(), None
        return from_table or from_intro

    parser = DocumentExtractor(targets)
    return parser(parse_color)


# TODO: Are there more formats?
def _get_sizes(soup):
    targets = [
        soup.find_all("span", {"class", "a-size-base swatch-title-text-display swatch-title-text"})[1:],
        soup.find_all("option", id=re.compile("size_name"))[1:],
    ]

    def parse_sizes(sizes):
        sizes = [size.text.strip() for size in sizes if size.text.strip()]
        return ", ".join(sizes)

    parser = DocumentExtractor(targets)
    return parser(parse_sizes)


def _get_brand(soup):
    targets = [
        soup.find("div", {"id": "bylineInfo_feature_div"}).a.text
    ]

    def parse_brand(brand):
        if brand.startswith("Besuche den "):
            return brand[len("Besuche den "):-len("-Store")]
        if brand.startswith("Marke: "):
            return brand[len("Marke: "):]

    parser = DocumentExtractor(targets)
    return parser(parse_brand) \
        or _find_from_details_section(soup, "Marke") \
        or _find_from_details_section(soup, "Hersteller")


def _get_description(soup):
    targets = [
        soup.find("div", {"id": "productDescription"}),
        soup.find("div", {"id": "feature-bullets"}),
    ]

    def parse_description(description):
        desc_paragraph = getattr(description, "p", None)
        desc_list = description.find_all("span")
        if desc_paragraph and desc_paragraph.p is not None:
            return desc_paragraph.p.get_text().strip()

        if desc_list:
            if "Mehr anzeigen" in desc_list[-1].text.strip():
                desc_list = desc_list[:-1]
            return ". ".join([li.text.strip() for li in desc_list])

    parser = DocumentExtractor(targets)
    return parser(parse_description)


def _find_from_details_section(soup, prop):
    product_details_list = soup.find("div", {"id": "detailBulletsWrapper_feature_div"})
    product_details_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})

    if product_details_list:
        parent = product_details_list.find("span", text=re.compile(f"^{prop}")).parent
        return parent.find_all("span")[1].text

    if product_details_table:
        parent = product_details_table.find("th", text=re.compile(f"\s+{prop}\s+"))
        if not parent:
            add_info_table = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
            parent = add_info_table.find("th", text=re.compile(f"{prop}")).parent
            return parent.find("td").text.strip()
        return parent.parent.find("td").text.strip().replace("\u200e", "")
