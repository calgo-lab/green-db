import json
from logging import getLogger
from typing import List, Optional
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import DUBLINCORE, JSON_LD, MICRODATA, ParsedPage
from ..utils import (
    check_none_or_alternative,
    safely_return_first_element,
    sustainability_labels_to_certificates,
)

logger = getLogger(__name__)

NUM_IMAGE_URLS = 3
IMAGE_ID_INDEX = 5


def extract_otto_de(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for otto.de

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    microdata = safely_return_first_element(parsed_page.schema_org.get(MICRODATA, [{}]))
    dublin_core = safely_return_first_element(parsed_page.schema_org.get(DUBLINCORE, [{}]))
    json_ld = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))

    properties = microdata.get("properties", {})

    name = properties.get("name")
    brand = properties.get("brand")
    gtin = properties.get("gtin13")

    offer = safely_return_first_element(offer := properties.get("offers", {}), offer)
    offer_properties = offer.get("properties", {})
    currency = offer_properties.get("priceCurrency")
    if price := offer_properties.get("price"):
        price = safely_return_first_element(price, price)

    # check for attributes in json_ld if above extraction fails
    name = check_none_or_alternative(name, json_ld.get("name"))
    description = json_ld.get("description")

    if description is None:
        first_element = safely_return_first_element(dublin_core.get("elements", [{}]))
        description = first_element.get("content")

    gtin = check_none_or_alternative(gtin, json_ld.get("gtin13"))
    brand = check_none_or_alternative(brand, json_ld.get("brand", {}).get("name"))

    offers = json_ld.get("offers", {})
    price = check_none_or_alternative(price, offers.get("price"))
    currency = check_none_or_alternative(currency, offers.get("priceCurrency"))

    # format description, because it sometimes includes html tags
    if description is not None:
        description = BeautifulSoup(description, "lxml").text.replace("  ", " ").strip()
    gtin = int(gtin) if type(gtin) == str and len(gtin) > 0 else None

    product_data = _get_product_data(parsed_page.beautiful_soup)
    parsed_url = urlparse(parsed_page.scraped_page.url)

    sustainability_labels = _get_sustainability(
        product_data, parsed_page.beautiful_soup, parsed_page.scraped_page.category
    )
    image_urls = _get_image_urls(product_data, parsed_url)[:NUM_IMAGE_URLS]

    if not image_urls:
        image_urls = _get_image_urls(json_ld, parsed_url, is_json_ld=True)

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
            colors=None,
            sizes=None,
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
    "bluesign® PRODUCT": CertificateType.BLUESIGN_PRODUCT,
    "Organic Content Standard 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Unterstützt Cotton made in Africa": CertificateType.COTTON_MADE_IN_AFRICA,
    "Fairtrade Cotton": CertificateType.FAIRTRADE_COTTON,
    "GOTS made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "MADE IN GREEN by OEKO-TEX®": CertificateType.MADE_IN_GREEN_OEKO_TEX,
    "Recycled Claim Standard blended": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    "Recycled Claim Standard 100": CertificateType.RECYCLED_CLAIM_STANDARD_100,
    "bioRe® Sustainable Textiles Standard": CertificateType.BIORE,
    "Cradle to Cradle Certified™ GOLD": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Cradle to Cradle Certified™ SILVER": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "Cradle to Cradle Certified™ BRONZE": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "FSC®": CertificateType.FOREST_STEWARDSHIP_COUNCIL,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "ENERGY STAR®": CertificateType.ENERGY_STAR,
    "Vegetabil gegerbtes Leder": CertificateType.OTHER,
    "[REE]CYCLED": CertificateType.OTHER,
    "Recyceltes Material": CertificateType.OTHER,
    "Primegreen": CertificateType.OTHER,
    "Bio-Baumwolle": CertificateType.OTHER,
    "Primeblue": CertificateType.OTHER,
    "BIONIC-FINISH®ECO (Rudolf Chemie)": CertificateType.OTHER,
    "Umweltfreundlicher Färbeprozess": CertificateType.OTHER,
    "TENCEL™ Lyocell": CertificateType.OTHER,
    "TENCEL™ Modal": CertificateType.OTHER,
    "LENZING™ ECOVERO™": CertificateType.OTHER,
    "REPREVE®": CertificateType.OTHER,
    "Nachhaltige Viskose": CertificateType.OTHER,
    "ECONYL©": CertificateType.OTHER,
    "Recycelter Kunststoff (Hartwaren)": CertificateType.OTHER,
    "Energieeffizientes Gerät": CertificateType.OTHER,
    "Birla Viscose": CertificateType.OTHER,
    "Bio-Siegel": CertificateType.OTHER,
    "[REE]GROW": CertificateType.OTHER,
    "SEAQUAL™": CertificateType.OTHER,
    "adidas: mit recycelten Materialien": CertificateType.OTHER,
    "adidas: mit Parley Ocean Plastic": CertificateType.OTHER,
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


def _get_image_urls(
    product_data: dict, parsed_url: ParseResult, is_json_ld: bool = False
) -> List[str]:
    """
    Helper function to extract the image URLs.

    Args:
        product_data (dict): Representation of the product data JSON, or a JSON_LD
        parsed_url (ParseResult): Parsed URL
        is_json_ld (bool): Whether the `product_data` is in JSON_LD format, default=False

    Returns:
        List[str]: `list` of image URLs
    """

    if is_json_ld:
        image_urls_long = product_data.get("image", [])[:NUM_IMAGE_URLS]
        image_ids = [img.split("/")[IMAGE_ID_INDEX] for img in image_urls_long]
    else:
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


def _get_sustainability_info(beautiful_soup: BeautifulSoup) -> List[str]:
    """
    Helper function that extracts the sustainability information from the parsed HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML of Product Website.

    Returns:
        list: includes found sustainability strings.
    """

    return_value = []

    for label_html in beautiful_soup.find_all(
        "figcaption", attrs={"class": "pdp_sustainability-sheet__label-name"}
    ):
        return_value.append(label_html.text.strip())

    return return_value


def _get_energy_labels(product_data: dict, beautiful_soup: BeautifulSoup) -> List[str]:
    """
    Helper function that extracts the EU_ENERGY_LABEL from the product_data json.

    Args:
        product_data (dict): Representation of the product data JSON
        beautiful_soup (BeautifulSoup): Parsed HTML of Product Website.
    Returns:
        List[str]: `list` of found energy_labels.
    """

    energy_labels: List[str] = []
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

    if not energy_labels:
        if energy_label := beautiful_soup.find("div", attrs={"class": "p_energyLabelScala200"}):
            energy_labels.append(energy_label.text)

    # Adding the prefix "EU Energy label" to allow automated mapping,
    # see file: core.sustainability_labels.sustainability_labels.json
    return [f"EU Energy label {letter}" for letter in energy_labels]


def _get_sustainability(
    product_data: dict, beautiful_soup: BeautifulSoup, product_category: str
) -> Optional[List[str]]:
    """
    Helper function that extracts the product's sustainability information.

    Args:
        product_data (dict): Representation of the product data JSON
        beautiful_soup (BeautifulSoup): Parsed HTML of Product Website.
        product_category (str): Product Category
    Returns:
        List[str]: Sorted `list` of found sustainability labels
    """
    energy_labels = _get_energy_labels(product_data, beautiful_soup)
    other_labels = _get_sustainability_info(beautiful_soup)

    certificate_strings = other_labels + energy_labels

    # Due to the `filter` being empty, we expect that in `sustainability_information_htmls` there
    # wouldn't be anything found for the non-sustainable products, so we set a default label
    # UNAVAILABLE, so the non-sustainable products can be distinguished from the other products.
    if not certificate_strings:
        return [CertificateType.UNAVAILABLE]

    return sustainability_labels_to_certificates(
        certificate_strings, _LABEL_MAPPING, product_category
    )
