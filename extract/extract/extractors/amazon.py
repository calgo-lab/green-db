# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]
import re
from logging import getLogger
from typing import Any, Callable, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from ..utils import sustainability_labels_to_certificates

logger = getLogger(__name__)


_LABEL_MAPPING = {
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Global Organic Textile Standard": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "Organic Content Standard 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard Blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Compact by Design (zertifiziert durch Amazon)": CertificateType.COMPACT_BY_DESIGN,
    "Natrue": CertificateType.NATRUE,
    "Cradle to Cradle Certified": CertificateType.CRADLE_TO_CRADLE,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "The Forest Stewardship Council": CertificateType.FOREST_STEWARDSHIP_COUNCIL,
    "Das offizielle Nordische Umweltzeichen": CertificateType.NORDIC_SWAN_ECOLABEL,
    "Reducing CO2": CertificateType.CARBON_TRUST_REDUCING,
}


def extract_amazon(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for amazon.de.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    soup = parsed_page.beautiful_soup

    name = soup.find("span", {"id": "productTitle"}).text.strip()
    color = _get_color(soup)
    size = _get_sizes(soup)
    price = _get_price(parsed_page)
    image_urls = _get_image_urls(soup)

    currency = "EUR"

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = [span.text for span in sustainability_spans]
    sustainability_labels = sustainability_labels_to_certificates(
        sustainability_texts, _LABEL_MAPPING
    )

    brand = _get_brand(soup, "de")
    description = _get_description(soup)
    asin = _find_from_details_section(soup, "ASIN")

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
            size=size,
            gtin=None,
            asin=asin,
        )

    except ValidationError as error:
        # TODO Handle Me!!
        # error contains relatively nice report why data is not valid
        logger.info(error)
        return None


def _handle_parse(targets: list, parse: Callable) -> Optional[Any]:
    """
    Helper function that handles the parsing of product attributes from the HTML.

    Args:
        targets (list): List of scans on the `BeautifulSoup` soup
        parse (Callable): Function that is processing the scan result

    Returns:
        Optional[str]: `str` object when the parsing succeeded, else `None`.
    """
    if any(targets):
        result = [target for target in targets if target][0]
        return parse(result)

    return None


def _get_color(soup: BeautifulSoup) -> Optional[str]:
    """
    Helper function that extracts the product's color.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[str]: `str` object with the color name. If nothing was found `None` is returned.
    """
    targets = [
        soup.find("span", {"class": "selection"}),
        soup.find("tr", {"class": re.compile("po-color")}),
    ]

    def parse_color(color: BeautifulSoup) -> Optional[str]:
        if color.name == "span":
            return color.text.strip()
        if color.name == "tr":
            return color.find_all("span")[1].text
        return None

    return _handle_parse(targets, parse_color)


def _get_image_urls(soup: BeautifulSoup) -> Optional[list[str]]:
    """
    Helper function that extracts the product's image urls.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[list[str]]: `list` object containing `str` objects representing the image urls.
            If nothing was found `None` or empty list is returned.
    """
    targets = [
        soup.find("div", {"id": "altImages"}).find_all("img"),
    ]

    def parse_image_urls(images: list[BeautifulSoup]) -> list[str]:
        image_urls = [
            image["src"]
            for image in images
            if not image["src"].endswith(".gif")
            and "play-button-overlay" not in image["src"]
            and "play-icon-overlay" not in image["src"]
            and "360_icon" not in image["src"]
        ]
        return image_urls

    return _handle_parse(targets, parse_image_urls)


def _get_sizes(soup: BeautifulSoup) -> Optional[str]:
    """
    Helper function that extracts the product's sizes.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[str]: `str` object containing all sizes. If nothing was found `None`.
    """
    targets = [
        soup.find_all("span", {"class", "a-size-base swatch-title-text-display swatch-title-text"})[
            1:
        ],
        soup.find_all("option", id=re.compile("size_name"))[1:],
    ]

    def parse_sizes(sizes: list[BeautifulSoup]) -> str:
        sizes = [size.text.strip() for size in sizes if size.text.strip()]
        return ", ".join(sizes)

    return _handle_parse(targets, parse_sizes)


def _get_price(parsed_page: ParsedPage) -> Optional[float]:
    """
    Helper function that extracts the product's price.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[float]: `float` object if a price is given, else `None`.
    """
    targets = [
        parsed_page.scraped_page.meta_information["amazon_price"],
    ]

    def parse_price(price: str) -> float:
        return float(price.replace(".", "").replace(",", "."))

    return _handle_parse(targets, parse_price)


def _get_brand(soup: BeautifulSoup, language: str) -> Optional[str]:
    """
    Helper function that extracts the product's brand.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[str]: `str` object if a brand was found, else `None`.
    """
    targets = [
        soup.find("div", {"id": "bylineInfo_feature_div"}).a.text,
    ]

    _LANGUAGE_LOCALES = {
        "de": {
            "info": ("Besuche den ", "-Store", "Marke: "),
            "table": ("Marke", "Hersteller"),
        },
    }

    def parse_brand(brand: str) -> Optional[str]:
        info_locales = _LANGUAGE_LOCALES[language]["info"]
        if brand.startswith(info_locales[0]):
            return brand[len(info_locales[0]) : -len(info_locales[1])]  # noqa
        if brand.startswith(info_locales[2]):
            return brand[len(info_locales[2]) :]  # noqa
        return None

    table_locales = _LANGUAGE_LOCALES[language]["table"]
    return (
        _handle_parse(targets, parse_brand)
        or _find_from_details_section(soup, table_locales[0])
        or _find_from_details_section(soup, table_locales[1])
    )


def _get_description(soup: BeautifulSoup) -> str:
    """
    Helper function that extracts the product's description.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        str: `str` object with the description. Empty if nothing was found.
    """
    targets = [
        soup.find("div", {"id": "productDescription"}),
        soup.find("div", {"id": "feature-bullets"}),
    ]

    def parse_description(description: BeautifulSoup) -> str:
        desc_paragraph = getattr(description, "p", None)
        desc_list = description.find_all("li")
        if desc_paragraph:
            return desc_paragraph.get_text().strip()
        if desc_list:
            spans = [span.text.strip() for span in desc_list if span.text.strip()]
            return ". ".join(spans)
        return ""

    return _handle_parse(targets, parse_description)


def _find_from_details_section(soup: BeautifulSoup, prop: str) -> Optional[str]:
    """
    Helper function that extracts the value from a column of the parsed HTML detail section.

    Args:
        soup (BeautifulSoup): Parsed HTML
        prop (str): Column name

    Returns:
        Optional[str]: `str` object if the property was found or `None` if it failed
    """
    product_details_list = soup.find("div", {"id": "detailBulletsWrapper_feature_div"})
    product_details_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})

    if product_details_list:
        parent = product_details_list.find("span", text=re.compile(f"^{prop}")).parent
        return parent.find_all("span")[1].text

    if product_details_table:
        parent = product_details_table.find("th", text=re.compile(r"\s+" + prop + r"\s+"))
        if not parent:
            additional_section = soup.find(
                "table", {"id": "productDetails_detailBullets_sections1"}
            )
            parent = additional_section.find("th", text=re.compile(f"{prop}")).parent
            return parent.find("td").text.strip()
        return parent.parent.find("td").text.strip().replace("\u200e", "")
