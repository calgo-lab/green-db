from requests_mock import Adapter

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore

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

    # original url: https://www.otto.de/p/privileg-family-edition-pyrolyse-backofen-pbwr6-op8v2-in-mit-2-fach-teleskopauszug-pyrolyse-selbstreinigung-50-monate-herstellergarantie-682285688/#variationId=682285928 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "electronics-fridge-old-energy-label.html"
    category = "FRIDGE"
    meta_information = {"family": "electronics"}

    scraped_page = read_test_html(
        timestamp=timestamp,
        source=source,
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
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=None,
        consumer_lifestage=None,
        name="Privileg Family Edition Pyrolyse Backofen »PBWR6 OP8V2 IN«, "
        "mit 2-fach-Teleskopauszug, Pyrolyse-Selbstreinigung, 50 Monate Herstellergarantie",
        description="Privileg Family Edition Pyrolyse Backofen »PBWR6 OP8V2 IN«, "
        "mit 2-fach-Teleskopauszug, Pyrolyse-Selbstreinigung, 50 Monate "
        "Herstellergarantie für 333,00€ bei OTTO",
        brand="Privileg Family Edition",
        sustainability_labels=[CertificateType.UNKNOWN],  # type: ignore[attr-defined]
        image_urls=[
            "https://i.otto.mock/i/otto/19651738",
            "https://i.otto.mock/i/otto/19651739",
            "https://i.otto.mock/i/otto/19651740",
        ],
        price=333.00,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=8003437938573,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
