from datetime import datetime

from tests.test_utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_ZALANDO
from core.domain import Product
from extract import extract_product


def test_zalando_basic() -> None:
    timestamp = datetime.strptime("2022-02-17 12:49", "%Y-%m-%d %H:%M")
    scraped_page = read_test_html(
        timestamp,
        "zalando",
        "t-shirt.html",
        "TSHIRT",
        {"family": "FASHION", "sustainability": "reusing_materials", "sex": "MALE"},
    )
    actual = extract_product(TABLE_NAME_SCRAPING_ZALANDO, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url="dummy_url",
        merchant="zalando",
        category="TSHIRT",
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
