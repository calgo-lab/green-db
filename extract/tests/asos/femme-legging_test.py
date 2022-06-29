from core.constants import TABLE_NAME_SCRAPING_ASOS_FR
from core.domain import (
    CertificateType,
    ConsumerLifestageType,
    CountryType,
    CurrencyType,
    GenderType,
    Product,
)
from extract import extract_product

from ..utils import read_test_html


def test_asos_basic() -> None:
    timestamp = "2022-03-29 13:21:00"
    url = "https://www.asos.com/fr/other-stories/other-stories-legging-de-yoga-cotele-densemble-en-tissu-recycle-beige-chine/prd/24068707"  # noqa
    source = "asos"
    merchant = "asos"
    country = CountryType.FR
    file_name = "legging.json"
    category = "PANT"
    gender = GenderType.FEMALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    meta_information = {
        "family": "FASHION",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        source=source,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_ASOS_FR, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        name="& Other Stories - Legging de yoga côtelé d'ensemble en tissu recyclé - Beige chiné",
        description="Legging par & Other Stories. Un modèle de notre sélection durable. "
        "Soutien-gorge vendu séparément. Taille haute. Taille élastiquée. Coupe "
        "moulante. Flatte la silhouette",
        brand="& Other Stories",
        sustainability_labels=[CertificateType.OTHER],  # type: ignore[attr-defined]
        price=49.0,
        currency=CurrencyType.EUR,
        image_urls=[
            "images.asos-media.com/products/other-stories-legging-de-yoga-cotele-densemble-en-tissu-recycle-beige-chine/24068707-1-beigemelange",  # noqa
            "images.asos-media.com/products/other-stories-legging-de-yoga-cotele-densemble-en-tissu-recycle-beige-chine/24068707-2",  # noqa
            "images.asos-media.com/products/other-stories-legging-de-yoga-cotele-densemble-en-tissu-recycle-beige-chine/24068707-3",  # noqa
            "images.asos-media.com/products/other-stories-legging-de-yoga-cotele-densemble-en-tissu-recycle-beige-chine/24068707-4",  # noqa
        ],
        colors=["Beige chiné"],
        sizes=["XS - FR 34-36", "S - FR 38-40", "M - FR 42-44", "L - FR 46"],
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
