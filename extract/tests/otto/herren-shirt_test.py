from requests_mock import Adapter

from core.constants import TABLE_NAME_SCRAPING_OTTO
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_otto_basic(requests_mock: Adapter) -> None:
    label_html = """
        <div class='prd_sustainabilityLayer__label'>
            <div class='prd_sustainabilityLayer__caption'> unknown label name </div>
            <div class='prd_sustainabilityLayer__description'> some description </div>
            <div class='prd_sustainabilityLayer__licenseNumber'> some license </div>
        </div>
    """
    requests_mock.register_uri("GET", "/product/sustainability/layerContent", text=label_html)

    # original_url = https://www.otto.de/p/h-i-s-rundhalsshirt-packung-3-tlg-3er-pack-mit-druck-1379261103/#variationId=1379261260
    url = "https://www.otto.mock/"
    timestamp = "2022-04-19 12:49:00"
    merchant = "otto"
    file_name = "herren-shirt.html"
    category = "SHIRT"
    meta_information = {"sex": "MALE", "family": "FASHION"}

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
        name="H.I.S Rundhalsshirt (Packung, 3-tlg., 3er-Pack) mit Druck",
        description="H.I.S Rundhalsshirt (Packung, 3-tlg., 3er-Pack) mit Druck für 29,"
                    "99€. Kontrastfarbenes Band mit HIS Schriftzug im Ausschnitt, Pflegeleichtes "
                    "Material bei OTTO",
        brand="H.I.S",
        sustainability_labels=["certificate:UNKNOWN"],
        image_urls=[
            'https://i.otto.mock/i/otto/05cb3291-9921-5253-85d0-1e97c3dd5b37',
            'https://i.otto.mock/i/otto/77656fe2-ac3f-5242-9bb0-61b5d2f768a6',
            'https://i.otto.mock/i/otto/7072f590-6798-549a-bf2d-e8e82c6a6ed5'],
        price=29.99,
        currency="EUR",
        color=None,
        size=None,
        gtin=8907890476439,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
