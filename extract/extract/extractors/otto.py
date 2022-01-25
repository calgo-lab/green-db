import json
from logging import getLogger
from typing import List, Optional
from urllib.parse import ParseResult, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import LabelIDType, Product

from ..parse import DUBLINCORE, MICRODATA, ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)

NUM_IMAGE_URLS = 3


def extract_otto(parsed_page: ParsedPage) -> Optional[Product]:
    microdata = parsed_page.schema_org.get(MICRODATA, [{}])
    microdata = safely_return_first_element(microdata)

    properties = microdata.get("properties", {})

    name = properties.get("name", None)
    brand = properties.get("brand", None)

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
_LABEL_MAPPING = {
    "Global Recycled Standard": LabelIDType.GRS.value,
    "Vegetabil gegerbtes Leder": LabelIDType.OTHER.value,
    "[REE]CYCLED": LabelIDType.OTHER.value,
    "Recyceltes Material": LabelIDType.OTHER.value,
    "bluesign® APPROVED": LabelIDType.BLUES_P.value,
    "Primegreen": LabelIDType.OTHER.value,
    "bluesign® PRODUCT": LabelIDType.BLUES_P.value,
    "Grüner Knopf": LabelIDType.GK.value,
    "Organic Content Standard blended": LabelIDType.OCS_BLENDED.value,
    "Bio-Baumwolle": LabelIDType.OTHER.value,
    "Unterstützt Cotton made in Africa": LabelIDType.CMIA.value,
    "Primeblue": LabelIDType.OTHER.value,
    "Fairtrade Cotton": LabelIDType.FT.value,
    "Responsible Down Standard": LabelIDType.RDS.value,
    "BIONIC-FINISH®ECO (Rudolf Chemie)": LabelIDType.OTHER.value,
    "GOTS organic": LabelIDType.GOTS.value,
    "Umweltfreundlicher Färbeprozess": LabelIDType.OTHER.value,
    "TENCEL™ Lyocell": LabelIDType.OTHER.value,
    "MADE IN GREEN by OEKO-TEX®": LabelIDType.MIG_OEKO_TEX.value,
    "LENZING™ ECOVERO™": LabelIDType.OTHER.value,
    "REPREVE®": LabelIDType.OTHER.value,
    "Nachhaltige Viskose": LabelIDType.OTHER.value,
    "ECONYL©": LabelIDType.OTHER.value,
    "GOTS made with organic materials": LabelIDType.GOTS.value,
    "Blauer Engel": LabelIDType.BE.value,
    "Recycled Claim Standard blended": LabelIDType.RCS_BLENDED.value,
    "Recycled Claim Standard 100": LabelIDType.RCS_100.value,
    "Recycelter Kunststoff (Hartwaren)": LabelIDType.OTHER.value,
    "Bio-Siegel": LabelIDType.OTHER.value,
    "": LabelIDType.OTHER.value,
}


def _get_product_data(beautiful_soup: BeautifulSoup) -> dict:
    product_data = beautiful_soup.find(attrs={"id": "productDataJson"})

    if product_data is None:
        # not a product page?
        return {}

    return json.loads(product_data.string.strip())


def _get_image_urls(product_data: dict, parsed_url: ParseResult) -> List[str]:
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


def _get_sustainability_info_urls(product_data: dict, parsed_url: ParseResult) -> List[str]:

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


def _get_sustainability_info(soup: BeautifulSoup) -> dict:
    return_value = dict()

    for label_html in soup.find_all("div", attrs={"class": "prd_sustainabilityLayer__label"}):
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


def _get_sustainability(product_data: dict, parsed_url: ParseResult) -> List[str]:
    sustainability_information_urls = _get_sustainability_info_urls(product_data, parsed_url)

    if sustainability_information_urls is None:
        return []

    labels = {}

    for label_info_url in sustainability_information_urls:
        sustainable_soup = BeautifulSoup(label_info_url, "html.parser")
        labels.update(_get_sustainability_info(sustainable_soup))

    return sorted({_LABEL_MAPPING.get(label, LabelIDType.UNKNOWN.value) for label in labels.keys()})
