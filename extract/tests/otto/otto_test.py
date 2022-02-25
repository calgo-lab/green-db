from requests_mock import Adapter
from tests.test_utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO
from core.domain import Product
from extract import extract_product


def test_otto_basic(requests_mock: Adapter) -> None:
    label_html = """
        <div class='prd_sustainabilityLayer__label'>
            <div class='prd_sustainabilityLayer__caption'> unknown label name </div>
            <div class='prd_sustainabilityLayer__description'> some description </div>
            <div class='prd_sustainabilityLayer__licenseNumber'> some license </div>
        </div>
    """
    requests_mock.register_uri("GET", "/product/sustainability/layerContent", text=label_html)

    url = "https://www.otto.mock/"
    timestamp = "2022-02-17 12:49:00"
    merchant = "otto"
    file_name = "damen-pullover.html"
    category = "SWEATER"
    meta_information = {"sex": "FEMALE", "family": "FASHION"}

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )

    actual = extract_product(TABLE_NAME_SCRAPING_OTTO, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="s.Oliver Strickpullover »Pullover« (1-tlg)",
        description="s.Oliver Strickpullover »Pullover« (1-tlg) für 29,99€. mit regulärer Passform,"
        " hat einen V-Ausschnitt, hat eine Rippblende am Ausschnitt bei OTTO",
        brand="s.Oliver",
        sustainability_labels=["UNKNOWN"],
        image_urls=[
            "https://i.otto.mock/i/otto/c5580e48-fb81-5e76-aec5-eb68201af88a",
            "https://i.otto.mock/i/otto/f9ac60e4-ab47-5ae1-a449-25d4fe3d9307",
            "https://i.otto.mock/i/otto/1979af3b-ee61-52cb-bd64-1642ab0a65a7",
        ],
        price=29.99,
        currency="EUR",
        color=None,
        size=None,
        gtin=4065208505739,
        asin=None,
    )
    assert actual == expected
