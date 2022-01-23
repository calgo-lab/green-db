from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import Product

from ..parse import JSON_LD, ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def extract_zalando(parsed_page: ParsedPage) -> Optional[Product]:
    if "/outfits/" in parsed_page.scraped_page.url:
        return None

    meta_data = safely_return_first_element(parsed_page.schema_org.get(JSON_LD, [{}]))

    name = meta_data.get("name", None)
    description = meta_data.get("description", None)
    brand = meta_data.get("brand", {}).get("name", None)
    color = meta_data.get("color", None)

    first_offer = safely_return_first_element(meta_data.get("offers", [{}]))
    currency = first_offer.get("priceCurrency", None)
    image_urls = meta_data.get("image", [])
    if price := first_offer.get("price", None):
        price = float(price)

    sustainability_labels = _get_sustainability(parsed_page.beautiful_soup)

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
            color=color,
            size=None,
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
    "Responsible Wool Standard": "RWS",
    "GOTS - organic": "GOTS",
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": "OTHER",
    "Hergestellt aus mindestens 20% recycelter Baumwolle": "OTHER",
    "Hergestellt aus 70-100% recycelten Materialien": "OTHER",
    "Organisch": "OTHER",
    "Hergestellt aus 50-70% biologischen Materialien": "OTHER",
    "Hergestellt aus recyceltem Polyester": "OTHER",
    "Weniger Verpackung": "OTHER",
    "Better Cotton Initiative": "BCI",
    "Hergestellt aus 50-70% recycelten Materialien": "OTHER",
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": "OTHER",
    "Hergestellt aus 30-50% recycelten Materialien": "OTHER",
    "Sustainable Textile Production (STeP) by OEKO-TEX®": "OEKOTEX",
    "Global Recycled Standard": "GRS",
    "Hergestellt aus mindestens 50% Lyocell": "OTHER",
    "Biologisch abbaubar": "OTHER",
    "GOTS - made with organic materials": "GOTS",
    "bluesign®": "BlueS",
    "Hergestellt mit recyceltem Plastik": "OTHER",
    "Fairtrade Certified Cotton": "FT",
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": "OTHER",
    "Responsible Down Standard": "RDS",
    "Hergestellt aus 70-100% biologischen Materialien": "OTHER",
    "Hergestellt aus recycelter Wolle": "OTHER",
    "OCS - Organic Blended Content Standard": "OCS",
    "OEKO-TEX® Made in Green": "OEKOTEX",
    "Cradle to Cradle Certified™ Silver": "CRADLE",
    "Waldschonend": "OTHER",
    "Hergestellt aus recyceltem Nylon": "OTHER",
    "Leather Working Group": "LWG",
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": "OTHER",
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": "OTHER",
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": "OTHER",
    "OCS - Organic Content Standard": "OCS",
    "Cradle to Cradle Certified™ Gold": "CRADLE",
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": "OTHER",
    "Zum Wohl der Tierwelt": "OTHER",
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": "OTHER",  # type: ignore
    "Natürlich": "OTHER",
    "Hergestellt aus recyceltem Gummi": "OTHER",
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": "OTHER",
    "": "OTHER",
}


def __get_sustainability_info(
    beautiful_soup: BeautifulSoup,
    title_attr: str,
    description_attr: str,
    headline: str = "Dieser Artikel erfüllt die folgenden Nachhaltigkeits-Kriterien:",
) -> Dict[str, str]:

    # this area is hidden by default, so we need to find the right one
    hidden_areas = [
        div
        for div in beautiful_soup.find_all("div", attrs={"style": "max-height:0"})
        if headline in div.text
    ]

    if hidden_areas:
        sustainability_info_parsed = hidden_areas[0]

        titles = sustainability_info_parsed.find_all(attrs={"data-testid": title_attr})
        descriptions = sustainability_info_parsed.find_all(attrs={"data-testid": description_attr})

        return {
            title.string: description.string for title, description in zip(titles, descriptions)
        }

    else:
        return {}


def _get_sustainability(
    beautiful_soup: BeautifulSoup,
    headline: str = "Dieser Artikel erfüllt die folgenden Nachhaltigkeits-Kriterien:",
) -> List[str]:

    data = {
        "labels": __get_sustainability_info(
            beautiful_soup=beautiful_soup,
            title_attr="certificate__title",
            description_attr="certificate__description",
            headline=headline,
        ),
        "impact": __get_sustainability_info(
            beautiful_soup=beautiful_soup,
            title_attr="cluster-causes__title",
            description_attr="cluster-causes__intro-statement",
            headline=headline,
        ),
        "aspects": __get_sustainability_info(
            beautiful_soup=beautiful_soup,
            title_attr="cause__title",
            description_attr="cause__description",
            headline=headline,
        ),
    }

    # TODO: At least we should know when something is found we did not mapped manually..
    return sorted({_LABEL_MAPPING.get(label, "OTHER") for label in data.get("labels", {}).keys()})
