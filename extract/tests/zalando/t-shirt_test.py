from core.constants import TABLE_NAME_SCRAPING_ZALANDO_DE
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


def test_zalando_basic() -> None:
    timestamp = "2022-07-07 10:00:00"
    url = "https://www.zalando.mock/"
    source = "zalando"
    merchant = "zalando"
    country = CountryType.DE
    file_name = "t-shirt.html"
    category = "TSHIRT"
    gender = GenderType.MALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    meta_information = {
        "family": "FASHION",
        "sustainability": "reusing_materials",
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
    actual = extract_product(TABLE_NAME_SCRAPING_ZALANDO_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        name="JAAMES TURNTABLES - T-Shirt print - acid black",
        description=" ARMEDANGELS JAAMES TURNTABLES - T-Shirt print - acid black für 14,90 € "
        "(2022-07-07) Gratisversand für Bestellungen im Wert von über 24,90 €",
        brand="ARMEDANGELS",
        sustainability_labels=[CertificateType.GOTS_ORGANIC],  # type: ignore[attr-defined]
        price=14.90,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://img01.ztat.net/article/spp-media-p1/d477156d601a4d37801c933c3c80fb45/"
            "4ec5b5c24c3d4e9fb4cd424d18003622.jpg?imwidth=103&filter=packshot"
        ],
        colors=["acid black/dunkelgrau"],
        sizes=None,
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
