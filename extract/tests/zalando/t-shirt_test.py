from core.constants import TABLE_NAME_SCRAPING_ZALANDO_DE
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_zalando_basic() -> None:
    timestamp = "2022-04-22 12:49:00"
    url = "https://www.zalando.mock/"
    merchant = "zalando"
    country = "DE"
    file_name = "t-shirt.html"
    category = "TSHIRT"
    meta_information = {
        "family": "FASHION",
        "sustainability": "reusing_materials",
        "sex": "MALE",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_ZALANDO_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        country=country,
        category=category,
        name="JAAMES TURNTABLES - T-Shirt print - acid black",
        description=" ARMEDANGELS JAAMES TURNTABLES - T-Shirt print - acid black für "
        "14,90\xa0€ (2022-04-22) versandkostenfrei bei Zalando bestellen.",
        brand="ARMEDANGELS",
        sustainability_labels=["certificate:GOTS_ORGANIC"],
        price=14.90,
        currency="EUR",
        image_urls=[
            "https://img01.ztat.net/article/spp-media-p1/d477156d601a4d37801c933c3c80fb45/"
            "4ec5b5c24c3d4e9fb4cd424d18003622.jpg?imwidth=103&filter=packshot"
        ],
        color=["acid black/dunkelgrau"],
        size=None,
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
