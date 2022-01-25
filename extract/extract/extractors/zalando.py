from logging import getLogger
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from pydantic import ValidationError

from core.domain import LabelIDType, Product

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
_LABEL_MAPPING = {
    "Responsible Wool Standard": LabelIDType.RWS.value,
    "GOTS - organic": LabelIDType.GOTS.value,
    "Hergestellt aus Wolle aus verantwortungsbewusster Landwirtschaft": LabelIDType.OTHER.value,
    "Hergestellt aus mindestens 20% recycelter Baumwolle": LabelIDType.OTHER.value,
    "Hergestellt aus 70-100% recycelten Materialien": LabelIDType.OTHER.value,
    "Organisch": LabelIDType.OTHER.value,
    "Hergestellt aus 50-70% biologischen Materialien": LabelIDType.OTHER.value,
    "Hergestellt aus recyceltem Polyester": LabelIDType.OTHER.value,
    "Weniger Verpackung": LabelIDType.OTHER.value,
    "Better Cotton Initiative": LabelIDType.BCI.value,
    "Hergestellt aus 50-70% recycelten Materialien": LabelIDType.OTHER.value,
    "Hergestellt aus mindestens 50% verantwortungsbewussten forstbasierten Materialien": LabelIDType.OTHER.value,  # noqa
    "Hergestellt aus 30-50% recycelten Materialien": LabelIDType.OTHER.value,
    "Sustainable Textile Production (STeP) by OEKO-TEX®": LabelIDType.STEP_OEKO_TEX.value,
    "Global Recycled Standard": LabelIDType.GRS.value,
    "Hergestellt aus mindestens 50% Lyocell": LabelIDType.OTHER.value,
    "Biologisch abbaubar": LabelIDType.OTHER.value,
    "GOTS - made with organic materials": LabelIDType.GOTS.value,
    "bluesign®": LabelIDType.BLUES_P.value,
    "Hergestellt mit recyceltem Plastik": LabelIDType.OTHER.value,
    "Fairtrade Certified Cotton": LabelIDType.FT.value,
    "Hergestellt aus Daunen aus verantwortungsbewusster Landwirtschaft": LabelIDType.OTHER.value,
    "Responsible Down Standard": LabelIDType.RDS.value,
    "Hergestellt aus 70-100% biologischen Materialien": LabelIDType.OTHER.value,
    "Hergestellt aus recycelter Wolle": LabelIDType.OTHER.value,
    "OCS - Organic Blended Content Standard": LabelIDType.OCS_BLENDED.value,
    "OEKO-TEX® Made in Green": LabelIDType.MIG_OEKO_TEX.value,
    "Cradle to Cradle Certified™ Silver": LabelIDType.CTC_T_SILVER.value,
    "Waldschonend": LabelIDType.OTHER.value,
    "Hergestellt aus recyceltem Nylon": LabelIDType.OTHER.value,
    "Leather Working Group": LabelIDType.LWG.value,
    "Hergestellt aus mindestens 20% innovativen Leder-Alternativen": LabelIDType.OTHER.value,
    "Hergestellt aus mindestens 50% Polyurethanen auf Wasserbasis": LabelIDType.OTHER.value,
    "Hergestellt aus mindestens 20% innovativen Materialien aus recyceltem Müll": LabelIDType.OTHER.value,  # noqa
    "OCS - Organic Content Standard": LabelIDType.OCS.value,
    "Cradle to Cradle Certified™ Gold": LabelIDType.CTC_T_GOLD.value,
    "Hergestellt aus mindestens 50% nachhaltigerer Baumwolle": LabelIDType.OTHER.value,
    "Zum Wohl der Tierwelt": LabelIDType.OTHER.value,
    "Hergestellt aus mindestens 20% innovativen ökologischen Alternativen zu fossilen Brennstoffen": LabelIDType.OTHER.value,  # noqa
    "Natürlich": LabelIDType.OTHER.value,
    "Hergestellt aus recyceltem Gummi": LabelIDType.OTHER.value,
    "Hergestellt aus LENZING™ TENCEL™, einem Eco-Material": LabelIDType.OTHER.value,
    "": LabelIDType.OTHER.value,
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

    return sorted(
        {
            _LABEL_MAPPING.get(label, LabelIDType.UNKNOWN.value)
            for label in data.get("labels", {}).keys()
        }
    )
