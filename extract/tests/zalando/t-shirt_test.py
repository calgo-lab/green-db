from core.constants import TABLE_NAME_SCRAPING_ZALANDO
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_zalando_basic() -> None:
    timestamp = "2022-02-17 12:49:00"
    url = "https://www.zalando.mock/"
    merchant = "zalando"
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
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_ZALANDO, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="JAAMES TURNTABLES - T-Shirt print - acid black",
        description=" ARMEDANGELS JAAMES TURNTABLES - T-Shirt print - acid black für "
        "14,90\xa0€ (2021-12-21) versandkostenfrei bei Zalando bestellen.",
        brand="ARMEDANGELS",
        sustainability_labels=["GOTS_ORGANIC"],
        price=14.90,
        currency="EUR",
        image_urls=[
            "https://img01.ztat.net/article/spp-media-p1/d477156d601a4d37801c933c3c80fb45/"
            "4ec5b5c24c3d4e9fb4cd424d18003622.jpg?imwidth=103&filter=packshot"
        ],
        color="acid black/dunkelgrau",
        size=None,
        gtin=None,
        asin=None,
    )
    assert actual == expected
