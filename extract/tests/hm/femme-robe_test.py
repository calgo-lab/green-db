from core.constants import TABLE_NAME_SCRAPING_HM_FR
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_hm_basic() -> None:
    timestamp = "2022-04-12 11:21:00"
    url = "https://www2.hm.com/fr_fr/productpage.1061531002.html"
    source = "hm"
    merchant = "hm"
    country = "FR"
    file_name = "femme-robe.html"
    category = "DRESS"
    gender = "FEMALE"
    consumer_lifestage = "ADULT"
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
        name="MAMA Robe avec ceinture à nouer",
        description="Robe de longueur mi-mollet en viscose tissée. Modèle avec encolure en V, "
        "boutonnage devant et manches courtes. Ceinture à nouer sous la poitrine. "
        "Fentes latérales. Non doublée.",
        brand="H&M",
        sustainability_labels=[
            "certificate:HIGG_INDEX_MATERIALS",
            "certificate:HM_CONSCIOUS",
            "certificate:OTHER",
        ],
        price=34.99,
        currency="EUR",
        image_urls=[
            "https://lp2.hm.com/hmgoepprod?set=quality%5B79%5D%2Csource%5B%2F9a%2F1d"
            "%2F9a1dcde9a8e1bfa9866256583cd0eef503d21f97.jpg%5D%2Corigin%5Bdam%5D%2Ccategory%5B"
            "%5D%2Ctype%5BLOOKBOOK%5D%2Cres%5Bm%5D%2Chmver%5B1%5D&call=url[file:/product/main]"
        ],
        colors=["Blanc"],
        sizes=["XS", "S", "M", "L", "XL", "XXL", "XS/P", "S/P", "M/P", "L/P", "XL/P", "XXL/P"],
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
