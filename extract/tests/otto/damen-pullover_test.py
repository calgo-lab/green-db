from requests_mock import Adapter
from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import (
    CertificateType,
    ConsumerLifestageType,
    CountryType,
    CurrencyType,
    GenderType,
    Product,
)

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_otto_basic(requests_mock: Adapter) -> None:
    label_html = """
        <div class='prd_sustainabilityLayer__label'>
            <div class='prd_sustainabilityLayer__caption'> bioRe® Sustainable Textiles Standard </div>
            <div class='prd_sustainabilityLayer__description'> some description </div>
            <div class='prd_sustainabilityLayer__licenseNumber'> some license </div>
        </div>
        <div class='prd_sustainabilityLayer__label'>
            <div class='prd_sustainabilityLayer__caption'> Fairtrade Cotton </div>
            <div class='prd_sustainabilityLayer__description'> some description </div>
            <div class='prd_sustainabilityLayer__licenseNumber'> some license </div>
        </div>
    """  # noqa
    requests_mock.register_uri("GET", "/product/sustainability/layerContent", text=label_html)

    url = "https://www.otto.mock/"
    timestamp = "2022-02-17 12:49:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "damen-pullover.html"
    category = "SWEATER"
    gender = GenderType.FEMALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    meta_information = {"family": "FASHION"}

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

    actual = extract_product(TABLE_NAME_SCRAPING_OTTO_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        name="s.Oliver Strickpullover »Pullover langarm«",
        description="Strickpulli mit Stehkragen",
        brand="s.Oliver",
        sustainability_labels=[CertificateType.UNAVAILABLE],  # type: ignore[attr-defined] # noqa
        image_urls=[
            "https://i.otto.mock/i/otto/81ee0cf2-df64-51a9-b91c-20d08b430704",
            "https://i.otto.mock/i/otto/b7e00734-7941-53d0-b1e6-5e7d599e8874",
            "https://i.otto.mock/i/otto/a24626eb-6f73-5b37-a708-cbadb612bcf3",
        ],
        price=32.19,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=4065208630462,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
