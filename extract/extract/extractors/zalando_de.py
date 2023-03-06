import json
import urllib
import xml.etree.ElementTree as ElementTree
from logging import getLogger
from typing import Any, Dict, Iterator, Optional

from pydantic import ValidationError

from core.domain import CertificateType, Product

from ..parse import JSON_LD, ParsedPage
from ..utils import (
    check_and_create_attributes_list,
    safely_return_first_element,
    sustainability_labels_to_certificates,
)

logger = getLogger(__name__)

_LABEL_MAPPING = {
    "": CertificateType.OTHER,
    "AppleSkin™ (Mabel Industries)": CertificateType.OTHER,
    "Argent Cradle to Cradle Certified® ": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "BASF E3": CertificateType.OTHER,
    "Better Cotton Initiative": CertificateType.BETTER_COTTON_INITIATIVE,
    "Biodégradable": CertificateType.OTHER,
    "Biologique": CertificateType.OTHER,
    "Biologisch abbaubar": CertificateType.OTHER,
    "Birla Viscose": CertificateType.OTHER,
    "Bronze Cradle to Cradle Certified®": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "Chrome-Free Tanned Leather": CertificateType.OTHER,
    "Circular Design Criteria by circular.fashion": CertificateType.OTHER,
    "Cradle to Cradle Certified ® Bronze": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "Cradle to Cradle Certified ® Gold": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Cradle to Cradle Certified ® Platinum": CertificateType.CRADLE_TO_CRADLE_PLATINUM,
    "Cradle to Cradle Certified ® Silver": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "Cradle to Cradle Certified™ Bronze": CertificateType.CRADLE_TO_CRADLE_BRONZE,
    "Cradle to Cradle Certified™ Gold": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Cradle to Cradle Certified™ Platinum": CertificateType.CRADLE_TO_CRADLE_PLATINUM,
    "Cradle to Cradle Certified™ Silver": CertificateType.CRADLE_TO_CRADLE_SILVER,
    "ECONYL® (Aquafil)": CertificateType.OTHER,
    "Eastman Naia™": CertificateType.OTHER,
    "Fabriqué avec 30-50% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec 50-70% de matériaux organiques": CertificateType.OTHER,
    "Fabriqué avec 50-70% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec 70-100% de matériaux organiques": CertificateType.OTHER,
    "Fabriqué avec 70-100% de matériaux recyclés": CertificateType.OTHER,
    "Fabriqué avec au moins 20 % d'alternatives biologiques innovantes aux combustibles fossiles": CertificateType.OTHER,  # noqa
    "Fabriqué avec au moins 20% d'alternatives innovantes au cuir": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de coton recyclé": CertificateType.OTHER,
    "Fabriqué avec au moins 20% de matériaux innovants recyclés à partir de déchets": CertificateType.OTHER,  # noqa
    "Fabriqué avec au moins 20% de matériaux issus de l'agriculture biologique régénératrice.": CertificateType.OTHER,  # noqa
    "Fabriqué avec au moins 50 % de polyuréthane à base d'eau": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de coton provenant de sources durables.": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de lyocell": CertificateType.OTHER,
    "Fabriqué avec au moins 50% de matériaux responsables issus de forêts": CertificateType.OTHER,
    "Fabriqué avec de la laine provenant de sources responsables": CertificateType.OTHER,
    "Fabriqué avec du duvet provenant de sources responsables": CertificateType.OTHER,
    "Fairtrade Certified Cotton": CertificateType.FAIRTRADE_COTTON,
    "Fairtrade Cotton": CertificateType.FAIRTRADE_COTTON,
    "Forest Stewardship Council (FSC)": CertificateType.FOREST_STEWARDSHIP_COUNCIL,
    "GOTS - made with organic materials": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,
    "GOTS - organic": CertificateType.GOTS_ORGANIC,
    "Global Organic Textile Standard (GOTS) - Made with Organic": CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS,  # noqa
    "Global Organic Textile Standard (GOTS) - Organic": CertificateType.GOTS_ORGANIC,
    "Global Organic Textile Standard (GOTS) - Organic In conversion": CertificateType.OTHER,
    "Global Recycle Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Global Recycled Standard": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Global Recycled Standard (GRS)": CertificateType.GLOBAL_RECYCLED_STANDARD,
    "Hergestellt aus 30-50% recycelten Materialien": CertificateType.OTHER,
    "Hergestellt aus 50-70% biologischen Materialien": CertificateType.OTHER,
    "Hergestellt aus 50-70% recycelten Materialien": CertificateType.OTHER,
    "Hergestellt aus 70-100% biologischen Materialien": CertificateType.OTHER,
    "Hergestellt aus 70-100% recycelten Materialien": CertificateType.OTHER,
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": CertificateType.OTHER,
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": CertificateType.OTHER,
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% Materialien aus regenerativem Bio-Anbau": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": CertificateType.OTHER,
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": CertificateType.OTHER,  # noqa
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": CertificateType.OTHER,  # noqa
    "Hergestellt aus mindestens 20% recycelter Baumwolle": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% Lyocell": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": CertificateType.OTHER,
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": CertificateType.OTHER,  # noqa
    "Hergestellt aus recyceltem Gummi": CertificateType.OTHER,
    "Hergestellt aus recyceltem Nylon": CertificateType.OTHER,
    "Hergestellt aus recyceltem Polyester": CertificateType.OTHER,
    "Hergestellt aus recycelter Wolle": CertificateType.OTHER,
    "Hergestellt mit recyceltem Plastik": CertificateType.OTHER,
    "LENZING™ ECOVERO™": CertificateType.OTHER,
    "LENZING™ Lyocell": CertificateType.OTHER,
    "LENZING™ Modal": CertificateType.OTHER,
    "LENZING™ Viscose": CertificateType.OTHER,
    "LIVA REVIVA (Birla Cellulose)": CertificateType.OTHER,
    "Livaeco (Birla Cellulose)": CertificateType.OTHER,
    "Lyocell": CertificateType.OTHER,
    "Made with 30-50% recycled materials": CertificateType.OTHER,
    "Made with 50-70% organic materials": CertificateType.OTHER,
    "Made with 50-70% recycled materials": CertificateType.OTHER,
    "Made with 70-100% organic materials": CertificateType.OTHER,
    "Made with 70-100% recycled materials": CertificateType.OTHER,
    "Made with at least 20% innovative bio-based alternatives to fossil fuels": CertificateType.OTHER,  # noqa
    "Made with at least 20% innovative leather alternatives": CertificateType.OTHER,
    "Made with at least 20% innovative materials upcycled from waste": CertificateType.OTHER,
    "Made with at least 20% materials from regenerative organic farming": CertificateType.OTHER,
    "Made with at least 20% recycled cotton": CertificateType.OTHER,
    "Made with at least 50% lyocell": CertificateType.OTHER,
    "Made with at least 50% responsible forest-based materials": CertificateType.OTHER,
    "Made with at least 50% sustainably-sourced cotton": CertificateType.OTHER,
    "Made with at least 50% water-based polyurethane": CertificateType.OTHER,
    "Made with responsibly-sourced down": CertificateType.OTHER,
    "Made with responsibly-sourced wool": CertificateType.OTHER,
    "Moins d’emballage": CertificateType.OTHER,
    "Naturel": CertificateType.OTHER,
    "Natürlich": CertificateType.OTHER,
    "OCS - Organic Blended Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "OCS - Organic Content Standard": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "OEKO-TEX® Made in Green": CertificateType.MADE_IN_GREEN_OEKO_TEX,
    "Or Cradle to Cradle Certified® ": CertificateType.CRADLE_TO_CRADLE_GOLD,
    "Organic": CertificateType.OTHER,
    "Organic Content Standard (OCS) - 100": CertificateType.ORGANIC_CONTENT_STANDARD_100,
    "Organic Content Standard (OCS) - Blended": CertificateType.ORGANIC_CONTENT_STANDARD_BLENDED,
    "Organic Content Standard (OCS) - Organic In conversion": CertificateType.OTHER,
    "Organisch": CertificateType.OTHER,
    'Other "Green Shirt" CanopyStyle Rated Man-Made Cellulosic Fiber': CertificateType.OTHER,
    "Other Remanufacturing/Recycling Process": CertificateType.OTHER,
    "Piñatex® (Ananas Anam)": CertificateType.OTHER,
    "Platine Cradle to Cradle Certified®": CertificateType.CRADLE_TO_CRADLE_PLATINUM,
    "RCotton (Recover™)": CertificateType.OTHER,
    "REPREVE® (Unifi)": CertificateType.OTHER,
    "Recycled Claim Standard (RCS) - 100": CertificateType.RECYCLED_CLAIM_STANDARD_100,
    "Recycled Claim Standard (RCS) - Blended": CertificateType.RECYCLED_CLAIM_STANDARD_BLENDED,
    "Respectueux des animaux": CertificateType.OTHER,
    "Respectueux des forêts": CertificateType.OTHER,
    "Responsible Mohair Standard": CertificateType.OTHER,
    "Responsible Wool Standard": CertificateType.RESPONSIBLE_WOOL_STANDARD,
    "SCS Recycled Content Certification": CertificateType.OTHER,
    "Sorona® (DUPONT)": CertificateType.OTHER,
    "Sustainable Textile Production (STeP) by OEKO-TEX®": CertificateType.STEP_OEKO_TEX,
    "TENCEL™ Lyocell (Lenzing)": CertificateType.OTHER,
    "TENCEL™ Modal (Lenzing)": CertificateType.OTHER,
    "Texloop™ (RCOT™)": CertificateType.OTHER,
    "Texlop™ (RCOT™)": CertificateType.OTHER,
    "USDA Certified Biobased": CertificateType.OTHER,
    "Waldschonend": CertificateType.OTHER,
    "Water-Based Polyurethane": CertificateType.OTHER,
    "Weniger Verpackung": CertificateType.OTHER,
    "ZQ Certified Merino Wool": CertificateType.OTHER,
    "ZQ Crtified Merino Wool": CertificateType.OTHER,
    "Zum Wohl der Tierwelt": CertificateType.OTHER,
    "bluesign® APPROVED materials": CertificateType.BLUESIGN_APPROVED,
}


def extract_zalando_de(
    parsed_page: ParsedPage, label_mapping: Dict[str, CertificateType] = _LABEL_MAPPING
) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for zalando.de and zalando.fr.

    Args:
        label_mapping: `label_mapping` for shop specific certificates strings
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

    sustainability_strings = get_sustainability_strings(parsed_page)
    sustainability_labels = sustainability_labels_to_certificates(
        sustainability_strings, label_mapping
    )

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
        Any: decoded json object
    """

    try:
        return json.loads(json_file)
    except json.decoder.JSONDecodeError:
        unquoted = ElementTree.fromstring(f"<root>{json_file}</root>").text
        return json.loads(unquoted or "")


def get_sustainability_strings(parsed_page: ParsedPage) -> Iterator[str]:
    """
    Extracts the sustainability information from HTML. Splash does not load all the information
    into the html anymore,so we have to extract the sustainability information from a JSON, stored
    inside a script tag.

    Args:
        parsed_page (ParsedPage): `ParsedPage` object

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
