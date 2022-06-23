from requests_mock import Adapter

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
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

    # original url: https://www.otto.de/p/casual-looks-rundhalsshirt-shirt-645503675/#variationId=144423297 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-04-20 15:14:00"
    merchant = "otto"
    country = "DE"
    file_name = "damen-shirt.html"
    category = "SHIRT"
    meta_information = {"sex": "FEMALE", "family": "FASHION"}

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )

    actual = extract_product(TABLE_NAME_SCRAPING_OTTO_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        country=country,
        category=category,
        name="Casual Looks Rundhalsshirt »Shirt«",
        description="Casual Looks Rundhalsshirt »Shirt« ab 12,99€. reine Baumwolle, gerade "
        "Schnittführung, figurfreundliche Schnittführung, angenehmer Tragekomfort bei"
        " OTTO",
        brand="Casual Looks",
        sustainability_labels=["certificate:UNKNOWN"],
        image_urls=[
            "https://i.otto.mock/i/otto/4c506363-076b-56e8-9521-ca9467f81d6c",
            "https://i.otto.mock/i/otto/df4d1d25-0e9f-5f68-9a7b-8596e65dab30",
            "https://i.otto.mock/i/otto/3be58871-7072-5a3c-9bb6-44dfd18fe4b1",
        ],
        price=12.99,
        currency="EUR",
        color=None,
        size=None,
        gtin=5205012107630,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
