import re
from enum import Enum
from logging import getLogger
from pathlib import PurePosixPath
from typing import Any, Callable, List, Optional
from urllib.parse import urlparse, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from ..utils import check_and_create_attributes_list, sustainability_labels_to_certificates

logger = getLogger(__name__)


_LABEL_MAPPING = {
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Global Organic Textile Standard": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "Organic Content Standard 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard Blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Compact by Design (zertifiziert durch Amazon)": CertificateType.COMPACT_BY_DESIGN,
    "Compact by Design (Certified by Amazon)": CertificateType.COMPACT_BY_DESIGN,
    "Natrue": CertificateType.NATRUE,
    "Cradle to Cradle Certified": CertificateType.CRADLE_TO_CRADLE,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "The Forest Stewardship Council": CertificateType.FOREST_STEWARDSHIP_COUNCIL,
    "Das offizielle Nordische Umweltzeichen": CertificateType.NORDIC_SWAN_ECOLABEL,
    "Reducing CO2": CertificateType.CARBON_TRUST_REDUCING,
    "The Nordic Swan Ecolabel": CertificateType.NORDIC_SWAN_ECOLABEL,
    "C02 compensé de ClimatePartner": CertificateType.CLIMATE_NEUTRAL_CLIMATE_PARTNER,
    "Pre-owned": CertificateType.OTHER,
    "Pre-owned Certified": CertificateType.OTHER,
    "TCO Certified": CertificateType.TCO,  # TODO: There are 2 additional types for phone and laptop
    "STANDARD 100 by OEKO-TEX": CertificateType.OEKO_TEX_100,
    "Recycled Claim Standard 100": CertificateType.RECYCLED_CLAIM_STANDARD_100,
    "Recycled Blended Claim Standard": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    "Recycled Claim Standard Blended": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    "STANDARD 100 de OEKO-TEX": CertificateType.OEKO_TEX_100,
    "STANDARD 100 von OEKO-TEX": CertificateType.OEKO_TEX_100,
    "Étiquetage Énergétique": CertificateType.OTHER,
}

_ENERGY_LABELS = {"Energielabel", "Energy Label"}


class _Language(Enum):
    de = "de"
    fr = "fr"
    en = "co.uk"


_LANGUAGE_LOCALE_INFO = {
    _Language.de: ("Besuche den ", "-Store", "Marke: "),
    _Language.fr: ("Visiter la boutique ", "Marque\xa0: "),
    _Language.en: ("Visit the ", " Store", "Brand: "),
}

_LANGUAGE_LOCALE_TABLE = {
    _Language.de: ("Marke", "Hersteller", "Brand"),
    _Language.fr: ("Marque", "Fabricant"),
    _Language.en: ("Brand", "Manufacturer"),
}


def extract_amazon_de(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for amazon.de.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    top_level_domain = re.sub(
        "www\.amazon\.", "", urlparse(parsed_page.scraped_page.url).netloc  # noqa
    )
    language = _Language(top_level_domain)
    soup = parsed_page.beautiful_soup

    # `find` returns `None` if element does not exist
    if name := soup.find("span", {"id": "productTitle"}):
        name = name.text.strip()

    colors = check_and_create_attributes_list(_get_color(soup))
    sizes = check_and_create_attributes_list(_get_sizes(soup))
    price = _get_price(parsed_page)
    image_urls = _get_image_urls(soup)

    currency = "GBP" if language == _Language.en else "EUR"

    sustainability_spans = soup.find_all("span", id=re.compile("CPF-BTF-Certificate-Name"))
    sustainability_texts = {span.text for span in sustainability_spans}

    if repairability_index := get_repairability_index(soup):
        sustainability_texts.add(repairability_index)

    if label_with_level := get_energy_label_level(soup):
        # check and remove Energy label strings that are extracted from CPF section
        sustainability_texts = sustainability_texts.difference(_ENERGY_LABELS)
        sustainability_texts.add(label_with_level)  # add Energy label with level

    sustainability_labels = sustainability_labels_to_certificates(
        sustainability_texts,
        _LABEL_MAPPING,
        parsed_page.scraped_page.source,
        parsed_page.scraped_page.category,
    )

    brand = _get_brand(soup, language)
    description = _get_description(soup)

    asin = _find_from_details_section(soup, "ASIN")

    try:
        return Product(
            timestamp=parsed_page.scraped_page.timestamp,
            url=parsed_page.scraped_page.url,
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


def get_repairability_index(soup: BeautifulSoup) -> Optional[str]:
    """
    Helper function that extracts the french repairability index if available.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[str]: `str` object with the repairability index. The string format complies with
        the naming convention of the index in the 'sustainability-labels.json'.
        If nothing was found `None` is returned.
    """

    if repairability_index := soup.find(id="repairabilityIndex_feature_div"):
        if repairability_index.find("img"):
            repairability_index = float(repairability_index.find("img").get("alt"))
            if repairability_index < 8:
                repairability_index = int(repairability_index // 2) * 2
                return f"French Repair Index: {repairability_index} - {repairability_index+1.9}"
            else:
                return "French Repair Index: 8 - 10"
    return None


def get_energy_label_level(soup: BeautifulSoup) -> Optional[str]:
    """
    Helper function that extracts the product's (new) EU energy label level. The level is not listed
    in the CPR section, so we have to extract it from somewhere else.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[str]: `str` object with the energy label level. If nothing was found `None` is
        returned.
    """

    if energy_efficiency := soup.find(id="energyEfficiency"):
        if energy_efficiency.find("text"):
            return "EU Energy label " + energy_efficiency.find("text").get_text().strip()
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


def _strip_image_url(url: str) -> str:
    """
    The images on product pages are usually resized and they might
    have overlays like watermarks and play buttons for video thumbnails.
    This function finds the url of the source image without additional processing applied.

    amazon image url syntax: (feb 2023)
    image processing instructions are stored in the filename
    as additional suffixes before the file extension.
    like this: https://something.amazon.com/some/path/some-image._some._processing._instructions.jpg


    for example
    https://m.media-amazon.com/images/I/215G7G0ZmtL._AC_SR38,50_.jpg
    will return https://m.media-amazon.com/images/I/215G7G0ZmtL.jpg but resized to 38x50

    images can have multiple instructions

    for example
    https://m.media-amazon.com/images/I/5125-zWFo-L._SX500_SY400._CR0,0,600,3000_BG255,0,255._BR-150._PKdp-play-icon-overlay__.jpg
    will return https://m.media-amazon.com/images/I/5125-zWFo-L.jpg
    but resized to 500x400
    then expanded to 600x3000 with a pink background
    and finally overlayed with a play button

    Args:
        url (str): the url of the image

    Returns:
        str: The url of the source image
    """
    scheme, netloc, path_string, query, fragment = urlsplit(url)
    path = PurePosixPath(path_string)
    stem = path.stem[: path.stem.index(".")]
    return urlunsplit((scheme, netloc, str(path.with_stem(stem)), query, fragment))


def _get_image_urls(soup: BeautifulSoup) -> Optional[list[str]]:
    """
    Helper function that extracts the product's image urls.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[list[str]]: `list` object containing `str` objects representing the image urls.
            If nothing was found `None` or empty list is returned.
    """

    def parse_image_urls(images: BeautifulSoup) -> list[str]:
        return [
            _strip_image_url(str(image["src"]))
            for image in images.find_all("img")
            if not image["src"].endswith(".gif")
            and "play-button-overlay" not in image["src"]
            and "play-icon-overlay" not in image["src"]
            and "360_icon" not in image["src"]
        ]

    images = soup.find("div", {"id": "altImages"}) or soup.find(
        "div", {"class": "unrolledScrollBox"}
    )
    if images:
        return parse_image_urls(images)
    return None


def _get_sizes(soup: BeautifulSoup) -> Optional[List[str]]:
    """
    Helper function that extracts the product's sizes.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        Optional[List[str]]: list of sizes. If nothing was found `None`.
    """
    sizes = (
        soup.find_all("span", {"class", "a-size-base swatch-title-text-display swatch-title-text"})[
            1:
        ]
        or soup.find_all("option", id=re.compile("size_name"))[1:]
    )
    return [size.text.strip() for size in sizes if size.text.strip()] if sizes else None


def _get_price(parsed_page: ParsedPage) -> Optional[float]:
    """
    Helper function that extracts the product's price.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[float]: `float` object if a price is given, else `None`.
    """
    if meta_info := parsed_page.scraped_page.meta_information:
        if price := meta_info.get("price", None):
            return float(price.replace(".", "").replace(",", "."))

    return None


def _get_brand(soup: BeautifulSoup, language: _Language) -> Optional[str]:
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

    def parse_brand(brand: str) -> Optional[str]:
        info_locales = _LANGUAGE_LOCALE_INFO[language]
        if brand.startswith(info_locales[0]):
            if language == _Language.de:
                return brand[len(info_locales[0]) : -len(info_locales[1])]  # noqa
            else:
                return brand[len(info_locales[0]) :]  # noqa
        if brand.startswith(info_locales[-1]):
            return brand[len(info_locales[-1]) :]  # noqa
        return None

    table_locales = _LANGUAGE_LOCALE_TABLE[language]
    return (
        _handle_parse(targets, parse_brand)
        or _find_from_details_section(soup, table_locales[0])
        or _find_from_details_section(soup, table_locales[1])
        or _find_from_details_section(soup, table_locales[2])
    )


def _get_description(soup: BeautifulSoup) -> str:
    """
    Helper function that extracts the product's description. If the product has feature-bullets and
    a productDescription both are concatenated. Otherwise either the feature-bullets or the
    productDescription is returned.

    Args:
        soup (BeautifulSoup): Parsed HTML

    Returns:
        str: `str` object with the description. Empty if nothing was found.
    """
    targets = [
        soup.find("div", {"id": "productDescription"}),
        soup.find("div", {"id": "feature-bullets"}),
    ]

    def parse_description(description: BeautifulSoup) -> Optional[str]:
        desc_paragraph = getattr(description, "p", None)
        if desc_paragraph:
            return desc_paragraph.get_text().strip()
        desc_list = description.find_all("li")
        if desc_list:
            spans = [span.text.strip() for span in desc_list if span.text.strip()]
            return ". ".join(spans)
        return None

    description = _handle_parse(targets[:1], parse_description)
    bullets = _handle_parse(targets[1:], parse_description)

    if description and bullets:
        return f"{bullets}. {description}"
    return description or bullets or ""


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
        try:
            parent = product_details_table.find("th", text=re.compile(r"\s+" + prop + r"\s+"))
            if not parent:
                additional_section = soup.find(
                    "table", {"id": "productDetails_detailBullets_sections1"}
                )
                parent = additional_section.find("th", text=re.compile(f"{prop}")).parent
                return parent.find("td").text.strip()
            return parent.parent.find("td").text.strip().replace("\u200e", "")
        except AttributeError:
            return None
    return None
