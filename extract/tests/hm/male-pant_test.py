from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_HM_FR
from core.domain import (
    CertificateType,
    ConsumerLifestageType,
    CountryType,
    CurrencyType,
    GenderType,
    Product,
)

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_hm_basic() -> None:
    timestamp = "2022-06-06 11:21:00"
    url = "https://www2.hm.com/fr_fr/productpage.1045436003.html"
    source = "hm"
    merchant = "hm"
    country = CountryType.FR
    file_name = "male-pant-wrong-encoding.html"
    category = "PANT"
    gender = GenderType.MALE
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
    actual = extract_product(TABLE_NAME_SCRAPING_HM_FR, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        name="Short en jean Hybrid Regular",
        description="Pantalon jogger 5 poches en denim extensible de coton mélangé. Modèle avec "
        "taille de hauteur classique soulignée par lien de serrage dissimulé devant "
        "et élastique habillé dans le dos. Braguette zippée surmontée d’un bouton. "
        "Jambes droites pour une bonne aisance de mouvement au niveau des cuisses et "
        "des genoux. Article bénéficiant de la technologie Lycra® Hybrid qui apporte "
        "une souplesse et un confort exceptionnels, sans pour autant renoncer à un "
        "aspect denim authentique.",
        brand="H&M",
        sustainability_labels=[
            CertificateType.HM_CONSCIOUS,  # type: ignore[attr-defined]
            CertificateType.OTHER,  # type: ignore[attr-defined]
        ],
        price=29.99,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://lp2.hm.com/hmgoepprod?set=quality%5B79%5D%2Csource%5B%2Fdd%2F3e"
            "%2Fdd3e47e1d6c7285c0a2e6ad00a79d577757e1330.jpg%5D%2Corigin%5Bdam%5D%2Ccategory%5B"
            "%5D%2Ctype%5BDESCRIPTIVESTILLLIFE%5D%2Cres%5Bm%5D%2Chmver%5B2%5D&call=url["
            "file:/product/main]",
        ],
        colors=["Noir"],
        sizes=[
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "36",
            "38",
            "40",
            "42",
            "28S",
            "29S",
            "30S",
            "31S",
            "32S",
            "33S",
            "34S",
            "36S",
        ],
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
