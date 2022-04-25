from core.constants import TABLE_NAME_SCRAPING_AMAZON
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_amazon_details_list() -> None:
    timestamp = "2022-04-21 19:00:00"
    url = "https://www.amazon.de/-/en/Amazon-Aware-Womens-Sherpa-Jacket/dp/B097HRF9QZ/ref=sr_1_11?c=ts&keywords=Damenjacken&qid=1650905329&refinements=p_n_cpf_eligible%3A22579885031&s=apparel&sr=1-11&ts_id=1981835031&th=1"  # noqa
    merchant = "amazon"
    file_name = "jacket-detail-list.html"
    category = "JACKET"
    meta_information = {
        "family": "FASHION",
        "sex": "FEMALE",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_AMAZON, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="Amazon Aware Women's 100% Recycled Polyester Sherpa Jacket",
        description="Better starts with Aware - everyday essentials, created in an environmentally conscious. Made from dense bonded faux lambskin, this sherpa jacket provides extra warmth and is particularly comfortable. Made from GRS certified (Global Recycled Standard) recycled polyester and certified by ClimatePartner as CO2 neutral. Learn more about our third-party sustainability certifications.",
        brand="Amazon Aware",
        sustainability_labels=["certificate:CLIMATE_NEUTRAL_CLIMATE_PARTNER", "certificate:GLOBAL_RECYCLED_STANDARD"],
        price=53.99,
        currency="EUR",
        image_urls=[
            'https://m.media-amazon.com/images/I/41HMMHUNHFL._AC_SR38,50_.jpg',
            'https://m.media-amazon.com/images/I/41pGMQ2F3YL._AC_SR38,50_.jpg',
            'https://m.media-amazon.com/images/I/318IlBZTEfL._AC_SR38,50_.jpg',
            'https://m.media-amazon.com/images/I/41Pqha49ClL._AC_SR38,50_.jpg',
            'https://m.media-amazon.com/images/I/414l4czY+cL._AC_SR38,50_.jpg',
            'https://m.media-amazon.com/images/I/31jfi8P1ecL._AC_SR38,50_.jpg',
        ],
        color="Pale Pink",
        size="XXS, XS, S, M, L, XL, XXL, 3XL, 4XL, 5XL, 6XL, 7XL",
        gtin=None,
        asin="B097HNBFF9",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]


def test_amazon_details_table() -> None:
    timestamp = "2022-04-21 19:00:00"
    url = "https://www.amazon.de/-/en/Hagl%C3%B6fs-Warming-Breathable-Stretch-Movable/dp/B085Z5BR7S/ref=sr_1_18?c=ts&keywords=Damenjacken&qid=1650905329&refinements=p_n_cpf_eligible%3A22579885031&s=apparel&sr=1-18&ts_id=1981835031&th=1"  # noqa
    merchant = "amazon"
    file_name = "jacket-detail-table.html"
    category = "JACKET"
    meta_information = {
        "family": "FASHION",
        "sex": "FEMALE",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_AMAZON, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="Haglöfs Women's fleece jacket, warm, breathable, stretchy, movable",
        description="Density inside with a knitted surface, this warm and comfortable inner fabric provides instant and reliable protection. Works just as well on a shirt, as part of your everyday life, used as a reliable layer under protective clothing in nature. Two zip pockets provide space for important items, and the hem can be adjusted with one hand for one hand for better warmth and a perfect fit. You will not quickly separate from this comfortable and reliable inner fabric with hood. Comfortable fleece fabric with a dense interior and a knitted surface that provides warmth and comfort. Front zip and a soft flap that prevents the two side pockets with zip. Flatlock seams on the entire clothes and prevents friction with just one hand.",
        brand="HAGLÖFS",
        sustainability_labels=["certificate:BLUESIGN_PRODUCT"],
        price=137.68,
        currency="EUR",
        image_urls=[
            'https://m.media-amazon.com/images/I/51I5NWQqKHL._AC_US40_.jpg',
            'https://m.media-amazon.com/images/I/518GpTlI8bL._AC_US40_.jpg',
            'https://m.media-amazon.com/images/I/51W2S3AVEXL._AC_US40_.jpg',
            'https://m.media-amazon.com/images/I/41zir-imKeL._AC_US40_.jpg',
            'https://m.media-amazon.com/images/I/51QfPa2cXsL._AC_US40_.jpg',
            'https://m.media-amazon.com/images/I/51gcBSpvoRL._AC_US40_.jpg',
        ],
        color="Backsteinrot",
        size="XS, M, XL, XXL, L",
        gtin=None,
        asin="B085ZR1N52",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
