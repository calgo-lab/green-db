# Since the Enum 'CertificateType' is dynamically generated, mypy can't know the attributes.
# For this reason, we ignore those errors here.
# type: ignore[attr-defined]

import json
from logging import getLogger
from typing import List, Optional
from urllib.parse import ParseResult, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import DUBLINCORE, JSON_LD, MICRODATA, ParsedPage
from ..utils import safely_return_first_element, sustainability_labels_to_certificates

logger = getLogger(__name__)

NUM_IMAGE_URLS = 3


def extract_otto(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for otto.de

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    microdata = safely_return_first_element(parsed_page.schema_org.get(MICRODATA, [{}]))
    properties = microdata.get("properties", {})

    name = properties.get("name", None)
    brand = properties.get("brand", None)

    if brand is None:
        json_ld = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))
        brand = json_ld.get("brand", {}).get("name", None)

    gtin = properties.get("gtin13", None)
    gtin = int(gtin) if type(gtin) == str and len(gtin) > 0 else None

    offer = safely_return_first_element(offer := properties.get("offers", {}), offer)
    offer_properties = offer.get("properties", {})
    currency = offer_properties.get("priceCurrency", None)
    if price := offer_properties.get("price", None):
        price = safely_return_first_element(price, price)

    dublin_core = safely_return_first_element(parsed_page.schema_org.get(DUBLINCORE, [{}]))

    first_element = safely_return_first_element(dublin_core.get("elements", [{}]))
    description = first_element.get("content", None)

    product_data = _get_product_data(parsed_page.beautiful_soup)
    parsed_url = urlparse(parsed_page.scraped_page.url)

    sustainability_labels = _get_sustainability(product_data, parsed_url)
    image_urls = _get_image_urls(product_data, parsed_url)[:NUM_IMAGE_URLS]

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
            color=None,
            size=None,
            gtin=gtin,
            asin=None,
        )

    except ValidationError as error:
        # TODO Handle Me!!
        # error contains relatively nice report why data ist not valid
        logger.info(error)
        return None


# TODO: How can we do this smart?
# See: https://www.otto.de/shoppages/nachhaltigkeit/nachhaltiges_engagement/umweltfreundlich-bestellen/anspruch-an-nachhaltige-artikel-und-siegel  # noqa
_LABEL_MAPPING = {
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Vegetabil gegerbtes Leder": CertificateType.OTHER,
    "[REE]CYCLED": CertificateType.OTHER,
    "Recyceltes Material": CertificateType.OTHER,
    "Primegreen": CertificateType.OTHER,
    "bluesign® PRODUCT": CertificateType.BLUESIGN_PRODUCT,
    "Organic Content Standard 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Bio-Baumwolle": CertificateType.OTHER,
    "Unterstützt Cotton made in Africa": CertificateType.COTTON_MADE_IN_AFRICA,
    "Primeblue": CertificateType.OTHER,
    "Fairtrade Cotton": CertificateType.FAIRTRADE_COTTON,
    "BIONIC-FINISH®ECO (Rudolf Chemie)": CertificateType.OTHER,
    "GOTS made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "Umweltfreundlicher Färbeprozess": CertificateType.OTHER,
    "TENCEL™ Lyocell": CertificateType.OTHER,
    "TENCEL™ Modal": CertificateType.OTHER,
    "MADE IN GREEN by OEKO-TEX®": CertificateType.MADE_IN_GREEN_OEKO_TEX,
    "LENZING™ ECOVERO™": CertificateType.OTHER,
    "REPREVE®": CertificateType.OTHER,
    "Nachhaltige Viskose": CertificateType.OTHER,
    "ECONYL©": CertificateType.OTHER,
    "Recycled Claim Standard blended": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    "Recycled Claim Standard 100": CertificateType.RECYCLED_CLAIM_STANDARD_100,
    "Recycelter Kunststoff (Hartwaren)": CertificateType.OTHER,
    "Bio-Siegel": CertificateType.OTHER,
    "bioRe® Sustainable Textiles Standard": CertificateType.BIORE,
    "[REE]GROW": CertificateType.OTHER,
    "Energieeffizientes Gerät": CertificateType.OTHER,
    "Birla Viscose": CertificateType.OTHER,
    "": CertificateType.OTHER,
}


def _get_product_data(beautiful_soup: BeautifulSoup) -> dict:
    """
    Helper function to extract the embedded product data JSON.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML

    Returns:
        dict: Representation of the product data JSON
    """
    product_data = beautiful_soup.find(attrs={"id": "productDataJson"})

    if product_data is None:
        # not a product page?
        return {}

    return json.loads(product_data.string.strip())


def _get_image_urls(product_data: dict, parsed_url: ParseResult) -> List[str]:
    """
    Helper function to extract the image URLs.

    Args:
        product_data (dict): Representation of the product data JSON
        parsed_url (ParseResult): Parsed URL

    Returns:
        List[str]: `list` of image URLs
    """
    image_ids = [
        image["id"]
        for variation in product_data.get("variations", {}).values()
        for image in variation.get("images", [])
        if "id" in image
    ]

    image_urls = [
        parsed_url._replace(
            netloc=parsed_url.netloc.replace("www.", "i."),
            path=f"/i/otto/{image_id}",
        )
        for image_id in image_ids
    ]

    return [url.geturl() for url in image_urls]


def _get_sustainability_info_htmls(product_data: dict, parsed_url: ParseResult) -> List[str]:
    """
    Helper function to get the sustainability information (as HTML). Otto fetches the sustainability
    information when the button is clicked. Therefore, we need to, firstly, find the URLs
    and, secondly, send a request to get the actual sustainability information (as HTMLs).

    Args:
        product_data (dict): Representation of the product data JSON
        parsed_url (ParseResult): Parsed URL

    Returns:
        List[str]: `list` of sustainability information as HTMLs
    """
    sustainabilities = [
        variation.get("sustainability", {})
        for variation in product_data.get("variations", {}).values()
        if variation
    ]

    detail_paths = [
        sustainability.get("detailsUrl", {})
        for sustainability in sustainabilities
        if sustainability
    ]

    detail_urls = {
        parsed_url._replace(path=path.replace("#ft5_slash#", "/")) for path in detail_paths if path
    }

    return [
        requests.get(details_url.geturl()).content.decode("utf-8") for details_url in detail_urls
    ]


def _get_sustainability_info(beautiful_soup: BeautifulSoup) -> dict:
    """
    Helper function that extracts the sustainability information from the parsed HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML of sustainability information

    Returns:
        dict: Mapping from name to description and license of the sustainability information.
            If nothing was found, empty `dict`.
    """
    return_value = dict()

    for label_html in beautiful_soup.find_all(
        "div", attrs={"class": "prd_sustainabilityLayer__label"}
    ):
        name = label_html.find("div", attrs={"class": "prd_sustainabilityLayer__caption"})
        description = label_html.find(
            "div", attrs={"class": "prd_sustainabilityLayer__description"}
        )
        license_number = label_html.find(
            "div", attrs={"class": "prd_sustainabilityLayer__licenseNumber"}
        )

        return_value[name.getText(separator=" ", strip=True)] = {
            "description": description.getText(separator=" ", strip=True)
            if description is not None
            else None,
            "license": license_number.getText(separator=" ", strip=True)
            if license_number is not None
            else None,
        }
    return return_value


def _get_energy_labels(product_data: dict) -> List[str]:
    """
    Helper function that extracts the EU_ENERGY_LABEL from the product_data json.

    Args:
        product_data (dict): Representation of the product data JSON

    Returns:
        List[str]: `list` of found energy_labels.
    """

    energy_labels = []
    json_values = [product_data]

    for json_value in json_values:
        match json_value:
            case {"showNewEnergyLabelInfoLayer": True, "energyEfficiencyClasses": [*attributes]}:
                for attribute in attributes:
                    energy_labels.append(attribute.get("energyLabel", {}).get("letter"))
            case {**json_object}:
                json_values += json_object.values()
            case [*json_array]:
                json_values += json_array

    # Adding the prefix "EU Energy label" to allow automated mapping,
    # see file: core.sustainability_labels.sustainability_labels.json
    return [f"EU Energy label {letter}" for letter in energy_labels]


def _get_sustainability(product_data: dict, parsed_url: ParseResult) -> List[str]:
    """
    Helper function that extracts the product's sustainability information.

    Args:
        product_data (dict): Representation of the product data JSON
        parsed_url (ParseResult): Parsed URL

    Returns:
        List[str]: Sorted `list` of found sustainability labels
    """
    sustainability_information_htmls = _get_sustainability_info_htmls(product_data, parsed_url)
    energy_labels = _get_energy_labels(product_data)

    if sustainability_information_htmls is None and energy_labels is None:
        return []

    labels = {}

    for sustainability_information_html in sustainability_information_htmls:
        sustainable_soup = BeautifulSoup(sustainability_information_html, "html.parser")
        labels.update(_get_sustainability_info(sustainable_soup))

    return sorted(
        sustainability_labels_to_certificates(list(labels.keys()) + energy_labels, _LABEL_MAPPING)
    )
