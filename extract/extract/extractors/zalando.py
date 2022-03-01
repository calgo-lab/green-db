from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import Certificates, Product

from ..parse import JSON_LD, ParsedPage
from ..utils import safely_return_first_element

logger = getLogger(__name__)


def extract_zalando(parsed_page: ParsedPage) -> Optional[Product]:
    """
    Extracts information of interest from HTML (and other intermediate representations)
    and returns `Product` object or `None` if anything failed. Works for zalando.de.

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
    color = meta_data.get("color", None)

    first_offer = safely_return_first_element(meta_data.get("offers", [{}]))
    currency = first_offer.get("priceCurrency", None)
    image_urls = meta_data.get("image", [])
    if price := first_offer.get("price", None):
        price = float(price)

    sustainability_labels = _get_sustainability(parsed_page.beautiful_soup)

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
# See: https://www.zalando.de/campaigns/about-sustainability/
_LABEL_MAPPING = {
    "Responsible Wool Standard": Certificates.RWS,
    "GOTS - organic": Certificates.GOTS_ORGANIC,
    "GOTS - made with organic materials": Certificates.GOTS_MWOM,
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": Certificates.OTHER,
    "Hergestellt aus mindestens 20% recycelter Baumwolle": Certificates.OTHER,
    "Hergestellt aus 70-100% recycelten Materialien": Certificates.OTHER,
    "Organisch": Certificates.OTHER,
    "Hergestellt aus 50-70% biologischen Materialien": Certificates.OTHER,
    "Hergestellt aus recyceltem Polyester": Certificates.OTHER,
    "Weniger Verpackung": Certificates.OTHER,
    "Better Cotton Initiative": Certificates.BCI,
    "Hergestellt aus 50-70% recycelten Materialien": Certificates.OTHER,
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": Certificates.OTHER,  # noqa
    "Hergestellt aus 30-50% recycelten Materialien": Certificates.OTHER,
    "Sustainable Textile Production (STeP) by OEKO-TEX®": Certificates.STEP_OEKO_TEX,
    "Global Recycled Standard": Certificates.GRS,
    "Hergestellt aus mindestens 50% Lyocell": Certificates.OTHER,
    "Biologisch abbaubar": Certificates.OTHER,
    "bluesign®": Certificates.OTHER,
    "Hergestellt mit recyceltem Plastik": Certificates.OTHER,
    "Fairtrade Certified Cotton": Certificates.FT_B,
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": Certificates.OTHER,
    "Responsible Down Standard": Certificates.RDS,
    "Hergestellt aus 70-100% biologischen Materialien": Certificates.OTHER,
    "Hergestellt aus recycelter Wolle": Certificates.OTHER,
    "OCS - Organic Blended Content Standard": Certificates.OCS_BLENDED,
    "OEKO-TEX® Made in Green": Certificates.MIG_OEKO_TEX,
    "Cradle to Cradle Certified™ Bronze": Certificates.CTC_T_BRONZE,
    "Cradle to Cradle Certified™ Gold": Certificates.CTC_T_GOLD,
    "Cradle to Cradle Certified™ Silver": Certificates.CTC_T_SILVER,
    "Cradle to Cradle Certified™ Platinum": Certificates.CTC_T_PLATIN,
    "Waldschonend": Certificates.OTHER,
    "Hergestellt aus recyceltem Nylon": Certificates.OTHER,
    "Leather Working Group": Certificates.LWG,
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": Certificates.OTHER,
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": Certificates.OTHER,
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": Certificates.OTHER,  # noqa
    "OCS - Organic Content Standard": Certificates.OCS_100,
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": Certificates.OTHER,
    "Zum Wohl der Tierwelt": Certificates.OTHER,
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": Certificates.OTHER,  # noqa
    "Natürlich": Certificates.OTHER,
    "Hergestellt aus recyceltem Gummi": Certificates.OTHER,
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": Certificates.OTHER,
    "": Certificates.OTHER,
}


def __get_sustainability_info(
    beautiful_soup: BeautifulSoup,
    title_attr: str,
    description_attr: str,
    headline: str = "Dieser Artikel erfüllt die folgenden Nachhaltigkeits-Kriterien:",
) -> Dict[str, str]:
    """
    Helper function to extract sustainability information.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML
        title_attr (str): HTML attr of title
        description_attr (str): HTML attr of description
        headline (str, optional): Headline on webpage. Defaults to
            "Dieser Artikel erfüllt die folgenden Nachhaltigkeits-Kriterien:".

    Returns:
        Dict[str, str]: `dict` with name and description of found sustainability information
    """

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
    """
    Extracts the sustainability information from HTML.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML
        headline (str, optional): Headline on webpage. Defaults to
            "Dieser Artikel erfüllt die folgenden Nachhaltigkeits-Kriterien:".

    Returns:
        List[str]: Ordered `list` of found sustainability labels
    """

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

    return sorted(
        {_LABEL_MAPPING.get(label, Certificates.UNKNOWN) for label in data.get("labels", {}).keys()}
    )
