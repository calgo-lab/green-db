import json
import re
from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import ParsedPage
from ..utils import sustainability_labels_to_certificates

logger = getLogger(__name__)


_website_url_template = "https://www.e.leclerc/fp/{product_name}-{sku}"

def extract_eleclerc_fr(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from html, which in this case is a json
    and returns `Product` object or `None` if anything failed. Works for asos.com.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    page_json = json.loads(parsed_page.scraped_page.html)
    name = page_json.get("label")

    unfolded = unfold_json(page_json)

    description = search_unfolded(unfolded, "description")
    if color := search_unfolded(unfolded, "couleur", retrieve_keys=["value", "label"]):
        colors = [color]
    else:
        colors = None
    image = search_unfolded(unfolded, "image1", retrieve_keys=["value", "url"])
    image_urls = [image]
    brand = search_unfolded(unfolded, "marque", retrieve_keys=["value", "label"])

    sustainability_texts = []
    if fr_index_score := search_unfolded(unfolded, "indice_reparabilite"):
        sustainability_texts.append(fr_repairability_score_to_label(fr_index_score))
    if eu_energy_score := search_unfolded(unfolded, "classe_efficacite_energetique_2021", retrieve_keys=["value", "label"]):
        sustainability_texts.append(f"EU Energy label {eu_energy_score}")

    # TODO: add Reconditionné extraction

    variant = page_json.get("variants", [])[0]
    url = _website_url_template.format(product_name=variant.get("slug"), sku=variant.get("sku"))

    offer = variant.get("offers", [])[0]
    if price := offer.get("basePrice", {}).get("price", {}).get("price"):
        price = float(price/100)
    currency = offer.get("currency", {}).get("code")

    if sustainability_texts is None:
        sustainability_labels = [CertificateType.UNAVAILABLE]
    else:
        if type(sustainability_texts) == str:
            sustainability_texts = [sustainability_texts]

        sustainability_labels = sustainability_labels_to_certificates(
            sustainability_texts,
            _LABEL_MAPPING,
            parsed_page.scraped_page.source,
            parsed_page.scraped_page.category,
        )

    try:
        return Product(
            timestamp=parsed_page.scraped_page.timestamp,
            url=url,
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
            sizes=None,
            gtin=None,
            asin=None,
        )

    except ValidationError as error:
        # TODO Handle Me!!
        # error contains relatively nice report why data ist not valid
        logger.info(error)
        return None


# TODO: How can we do this smart?
_LABEL_MAPPING = {
    "": CertificateType.OTHER,
}


def fr_repairability_score_to_label(score):
    if score < 8:
        score = int(score // 2) * 2
        return f"French Repair Index: {score} - {score + 1.9}"
    else:
        return "French Repair Index: 8 - 10"


def unfold_json(data):
    json_values = [data]
    for json_value in json_values:
        match json_value:
            case {**json_object}:
                json_values += json_object.values()
            case [*json_array]:
                json_values += json_array
    return json_values


def search_unfolded(unfolded_json, value_constraint, key_constraint="code", retrieve_keys=["value"]):
    for item in unfolded_json:
        if type(item) == dict and item.get(key_constraint)==value_constraint:
            for key in retrieve_keys:
                item = item.get(key, {})
            return item
    return None
