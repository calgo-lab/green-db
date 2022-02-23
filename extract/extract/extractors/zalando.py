from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import LabelIDType, Product

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
    "Responsible Wool Standard": LabelIDType.RWS,
    "GOTS - organic": LabelIDType.GOTS_ORGANIC,
    "GOTS - made with organic materials": LabelIDType.GOTS_MWOM,
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": LabelIDType.OTHER,
    "Hergestellt aus mindestens 20% recycelter Baumwolle": LabelIDType.OTHER,
    "Hergestellt aus 70-100% recycelten Materialien": LabelIDType.OTHER,
    "Organisch": LabelIDType.OTHER,
    "Hergestellt aus 50-70% biologischen Materialien": LabelIDType.OTHER,
    "Hergestellt aus recyceltem Polyester": LabelIDType.OTHER,
    "Weniger Verpackung": LabelIDType.OTHER,
    "Better Cotton Initiative": LabelIDType.BCI,
    "Hergestellt aus 50-70% recycelten Materialien": LabelIDType.OTHER,
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": LabelIDType.OTHER,  # noqa
    "Hergestellt aus 30-50% recycelten Materialien": LabelIDType.OTHER,
    "Sustainable Textile Production (STeP) by OEKO-TEX®": LabelIDType.STEP_OEKO_TEX,
    "Global Recycled Standard": LabelIDType.GRS,
    "Hergestellt aus mindestens 50% Lyocell": LabelIDType.OTHER,
    "Biologisch abbaubar": LabelIDType.OTHER,
    "bluesign®": LabelIDType.OTHER,
    "Hergestellt mit recyceltem Plastik": LabelIDType.OTHER,
    "Fairtrade Certified Cotton": LabelIDType.FT_B,
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": LabelIDType.OTHER,
    "Responsible Down Standard": LabelIDType.RDS,
    "Hergestellt aus 70-100% biologischen Materialien": LabelIDType.OTHER,
    "Hergestellt aus recycelter Wolle": LabelIDType.OTHER,
    "OCS - Organic Blended Content Standard": LabelIDType.OCS_BLENDED,
    "OEKO-TEX® Made in Green": LabelIDType.MIG_OEKO_TEX,
    "Cradle to Cradle Certified™ Bronze": LabelIDType.CTC_T_BRONZE,
    "Cradle to Cradle Certified™ Gold": LabelIDType.CTC_T_GOLD,
    "Cradle to Cradle Certified™ Silver": LabelIDType.CTC_T_SILVER,
    "Cradle to Cradle Certified™ Platinum": LabelIDType.CTC_T_PLATIN,
    "Waldschonend": LabelIDType.OTHER,
    "Hergestellt aus recyceltem Nylon": LabelIDType.OTHER,
    "Leather Working Group": LabelIDType.LWG,
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": LabelIDType.OTHER,
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": LabelIDType.OTHER,
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": LabelIDType.OTHER,  # noqa
    "OCS - Organic Content Standard": LabelIDType.OCS_100,
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": LabelIDType.OTHER,
    "Zum Wohl der Tierwelt": LabelIDType.OTHER,
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": LabelIDType.OTHER,  # noqa
    "Natürlich": LabelIDType.OTHER,
    "Hergestellt aus recyceltem Gummi": LabelIDType.OTHER,
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": LabelIDType.OTHER,
    "": LabelIDType.OTHER,
}


def __get_sustainability_info(
    beautiful_soup: BeautifulSoup, title_attr: str, description_attr: str, certificate_attr: str
) -> Dict[str, str]:
    """
    Helper function to extract sustainability information.

    Args:
        beautiful_soup (BeautifulSoup): Parsed HTML
        title_attr (str): HTML attr of title
        description_attr (str): HTML attr of description
        certificate_attr (str): HTML attr of certificate section

    Returns:
        Dict[str, str]: `dict` with name and description of found sustainability information
    """

    sustainability_info_parsed = beautiful_soup.find("div", attrs={"data-testid": certificate_attr})
    if not sustainability_info_parsed:
        return {}

    titles = sustainability_info_parsed.find_all(attrs={"data-testid": title_attr})
    descriptions = sustainability_info_parsed.find_all(attrs={"data-testid": description_attr})

    return {title.string: description.string for title, description in zip(titles, descriptions)}


def _get_sustainability(
    beautiful_soup: BeautifulSoup,
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
            certificate_attr="cluster-certificates",
        ),
        "impact": __get_sustainability_info(
            beautiful_soup=beautiful_soup,
            title_attr="cluster-causes__title",
            description_attr="cluster-causes__intro-statement",
            certificate_attr="cluster-certificates",
        ),
        "aspects": __get_sustainability_info(
            beautiful_soup=beautiful_soup,
            title_attr="cause__title",
            description_attr="cause__description",
            certificate_attr="cluster-certificates",
        ),
    }

    return sorted(
        {_LABEL_MAPPING.get(label, LabelIDType.UNKNOWN) for label in data.get("labels", {}).keys()}
    )
