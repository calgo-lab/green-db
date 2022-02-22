from core.domain import Product
from extract import extract_product
from tests.test_utils import read_test_html
from extract.extractors.zalando import extract_zalando


def test_zalando_basic() -> None:
    page = read_test_html("zalando", "t-shirt.html", "TSHIRT")
    actual = extract_product(extract_zalando, page)
    expected = Product(
        url="dummy_url",
        merchant="zalando",
        categories="TSHIRT",
        name="JAAMES TURNTABLES - T-Shirt print - acid black",
        description=" ARMEDANGELS JAAMES TURNTABLES - T-Shirt print - acid black f\u00fcr "
        "14,90\u00a0\u20ac (2021-12-21) versandkostenfrei bei Zalando bestellen.",
        brand="ARMEDANGELS",
        sustainability_labels=["GOTS"],
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
