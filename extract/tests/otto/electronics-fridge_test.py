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

    # original url: https://www.otto.de/p/samsung-side-by-side-rs6ga884csl-178-cm-hoch-91-2-cm-breit-1524534276/#variationId=1524535294 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    merchant = "otto"
    country = "DE"
    file_name = "electronics-fridge.html"
    category = "FRIDGE"
    meta_information = {"family": "electronics"}

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
        name="Samsung Side-by-Side RS6GA884CSL, 178 cm hoch, 91,2 cm breit",
        description="Samsung Side-by-Side RS6GA884CSL, 178 cm hoch, 91,2 cm breit für 1.999,"
        "00€. Nutzinhalt: 635 Liter, No Frost – nie wieder abtauen!, Metal Cooling "
        "bei OTTO",
        brand="Samsung",
        sustainability_labels=["certificate:EU_ENERGY_LABEL_C"],
        image_urls=[
            "https://i.otto.mock/i/otto/02f85090-393a-5bd1-b56a-bac9f66295f7",
            "https://i.otto.mock/i/otto/e1f3b715-0081-5df1-9d50-14c19bc476e8",
            "https://i.otto.mock/i/otto/5d309975-6917-5f9e-b206-a1c99e83411c",
        ],
        price=1999.00,
        currency="EUR",
        colors=None,
        sizes=None,
        gtin=8806092536593,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
