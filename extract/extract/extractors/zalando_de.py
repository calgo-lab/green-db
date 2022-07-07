# type: ignore[attr-defined]

import json
import urllib
from datetime import datetime
from logging import getLogger
from typing import Dict, Iterator, Optional

from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import JSON_LD, ParsedPage
from ..utils import check_and_create_attributes_list, safely_return_first_element

logger = getLogger(__name__)

_LABEL_MAPPING = {
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "GOTS - organic": CertificateType.GOTS_ORGANIC,
    "GOTS - made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% recycelter Baumwolle": CertificateType.OTHER,
    "Hergestellt aus 70-100% recycelten Materialien": CertificateType.OTHER,
    "Organisch": CertificateType.OTHER,
    "Hergestellt aus 50-70% biologischen Materialien": CertificateType.OTHER,
    "Hergestellt aus recyceltem Polyester": CertificateType.OTHER,
    "Weniger Verpackung": CertificateType.OTHER,
    "Better Cotton Initiative": CertificateType.BETTER_COTTON_INITIATIVE,
    "Hergestellt aus 50-70% recycelten Materialien": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": CertificateType.OTHER,  # noqa
    "Hergestellt aus 30-50% recycelten Materialien": CertificateType.OTHER,
    "Sustainable Textile Production (STeP) by OEKO-TEX®": CertificateType.STEP_OEKO_TEX,
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Hergestellt aus mindestens 50% Lyocell": CertificateType.OTHER,
    "Biologisch abbaubar": CertificateType.OTHER,
    "bluesign®": CertificateType.OTHER,
    "Hergestellt mit recyceltem Plastik": CertificateType.OTHER,
    "Fairtrade Certified Cotton": CertificateType.FAIRTRADE_COTTON,
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": CertificateType.OTHER,
    "Responsible Down Standard": CertificateType.RESPONSIBLE_DOWN_STANDARD,
    "Hergestellt aus 70-100% biologischen Materialien": CertificateType.OTHER,
    "Hergestellt aus recycelter Wolle": CertificateType.OTHER,
    "OCS - Organic Blended Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "OEKO-TEX® Made in Green": CertificateType.MADE_IN_GREEN_OEKO_TEX,
    "Cradle to Cradle Certified™ Bronze": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "Cradle to Cradle Certified™ Gold": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Cradle to Cradle Certified™ Silver": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "Cradle to Cradle Certified™ Platinum": CertificateType.CRADLE_TO_CRADLE_PLATINUM,
    "Waldschonend": CertificateType.OTHER,
    "Hergestellt aus recyceltem Nylon": CertificateType.OTHER,
    "Leather Working Group": CertificateType.LEATHER_WORKING_GROUP,
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": CertificateType.OTHER,  # noqa
    "OCS - Organic Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": CertificateType.OTHER,
    "Zum Wohl der Tierwelt": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": CertificateType.OTHER,  # noqa
    "Natürlich": CertificateType.OTHER,
    "Hergestellt aus recyceltem Gummi": CertificateType.OTHER,
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": CertificateType.OTHER,
    "": CertificateType.OTHER,
}


def extract_zalando_de(
    parsed_page: ParsedPage, label_mapping: Dict[str, CertificateType] = _LABEL_MAPPING
) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for zalando.de and zalando.fr.

    Args:
        parsed_page (ParsedPage): Intermediate representation of `ScrapedPage` domain object

    Returns:
        Optional[Product]: Valid `Product` object or `None` if extraction failed
    """
    if "/outfits/" in parsed_page.scraped_page.url:
        return None

    meta_data = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))

    name = meta_data.get("name", None)
    description = meta_data.get("description", None)
    brand = meta_data.get("brand", {}).get("name", None)
    colors = check_and_create_attributes_list(meta_data.get("color", None))

    first_offer = safely_return_first_element(meta_data.get("offers", [{}]))
    currency = first_offer.get("priceCurrency", None)
    image_urls = meta_data.get("image", [])
    if price := first_offer.get("price", None):
        price = float(price)

    sustainability_strings = set(get_sustainability_strings(parsed_page))
    sustainability_labels = sorted(
        {
            label_mapping.get(sustainability_string, CertificateType.UNKNOWN)
            for sustainability_string in sustainability_strings
        }
    )

    if unknown_labels := {
        sustainability_string
        for sustainability_string in sustainability_strings
        if sustainability_string not in label_mapping
    }:
        logger.info(f'unknown sustainability labels: {", ".join(map(repr, unknown_labels))}')

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
            sizes=None,
            gtin=None,
            asin=None,
        )

    except ValidationError as error:
        # TODO Handle Me!!
        # error contains relatively nice report why data ist not valid
        logger.info(error)
        return None


def get_json_data(json_file: str) -> Any:
    """
    Helper function to parse mangled json files.
    
    Args:
        json_file (str): Either a plain json file or a json file encoded as an xml CDATA string

    Returns:
        Iterator[str]: found sustainability strings
    """
    
    try:
        return json.loads(json_file)
    except:
        json_file = ElementTree.fromstring(f'<root>{json_file}</root>').text
        return json.loads(json_file)


def get_sustainability_strings(parsed_page: ParsedPage) -> Iterator[str]:
    """
    Extracts the sustainability information from HTML. Splash does not load all the information
    into the html anymore,so we have to extract the sustainability information from a JSON, stored
    inside a script tag.

    Args:
        parsed_page (ParsedPage): Parsed Page

    Returns:
        Iterator[str]: found sustainability strings
    """
    
    # Loop over all JSON objects on the page to find sustainability information
    for json_file in parsed_page.beautiful_soup.findAll("script", {"type": "application/json"}):
        json_values = [get_json_data(json_file.get_text())]
        for json_value in json_values:
            match json_value:
                case {"sustainabilityClusterKind": "certificates", "attributes": [*attributes]}:
                    for attribute in attributes:
                        if "label" in attribute:
                            yield urllib.parse.unquote(attribute["label"])
                case {**json_object}:
                    json_values += json_object.values()
                case [*json_array]:
                    json_values += json_array
