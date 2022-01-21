import json
from typing import List, Optional
from urllib.parse import ParseResult, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import Product

from ..parse import DUBLINCORE, MICRODATA, ParsedPage
from ..utils import safely_return_first_element

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
            start_timestamp=parsed_page.scraped_page.start_timestamp,
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
        return None


# TODO: How can we do this smart?
_LABEL_MAPPING = {
    "Global Recycled Standard": "GRS",
    "Vegetabil gegerbtes Leder": "OTHER",
    "[REE]CYCLED": "OTHER",
    "Recyceltes Material": "OTHER",
    "bluesign® APPROVED": "BlueS",
    "Primegreen": "OTHER",
    "bluesign® PRODUCT": "BlueS",
    "Grüner Knopf": "GK",
    "Organic Content Standard blended": "OCS",
    "Bio-Baumwolle": "OTHER",
    "Unterstützt Cotton made in Africa": "CmiA",
    "Primeblue": "OTHER",
    "Fairtrade Cotton": "FT",
    "Responsible Down Standard": "RDS",
    "BIONIC-FINISH®ECO (Rudolf Chemie)": "OTHER",
    "GOTS organic": "GOTS",
    "Umweltfreundlicher Färbeprozess": "OTHER",
    "TENCEL™ Lyocell": "OTHER",
    "MADE IN GREEN by OEKO-TEX®": "OEKOTEX",
    "LENZING™ ECOVERO™": "OTHER",
    "REPREVE®": "OTHER",
    "Nachhaltige Viskose": "OTHER",
    "ECONYL©": "OTHER",
    "GOTS made with organic materials": "GOTS",
    "Blauer Engel": "BE",
    "Recycled Claim Standard blended": "RCS",
    "Recycled Claim Standard 100": "RCS",
    "Recycelter Kunststoff (Hartwaren)": "OTHER",
    "Bio-Siegel": "OTHER",
    "": "OTHER",
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

    # TODO: At least we should know when something is found we did not mapped manually..
    return sorted({_LABEL_MAPPING.get(label, "OTHER") for label in labels.keys()})
