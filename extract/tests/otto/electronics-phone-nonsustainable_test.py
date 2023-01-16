from requests_mock import Adapter
from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_otto_basic(requests_mock: Adapter) -> None:
    label_html = ""
    requests_mock.register_uri("GET", "/product/sustainability/layerContent", text=label_html)

    # original url: https://www.otto.de/p/sony-xperia-1-iii-5g-256gb-smartphone-16-51-cm-6-5-zoll-256-gb-speicherplatz-12-mp-kamera-C1397609879/#variationId=1397609888 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "electronics-phone-nonsustainable.html"
    category = "SMARTPHONE"
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
        name="Sony Xperia 1 III 5G, 256GB Smartphone (16,51 cm/6,5 Zoll, 256 GB Speicherplatz, "
        "12 MP Kamera)",
        description="Tolle Angebote und Top Qualität entdecken - CO2 neutraler Versand ✔ "
        "Kauf auf Rechnung und Raten ✔ Erfülle dir deine Wünsche bei OTTO!",
        brand="Sony",
        sustainability_labels=[CertificateType.UNAVAILABLE],  # type: ignore[attr-defined] # noqa
        image_urls=[
            "https://i.otto.mock/i/otto/eb2cc281-4f81-5c21-89ac-21235628df4a",
            "https://i.otto.mock/i/otto/f301b567-267d-5547-a4f1-27864f9cd864",
            "https://i.otto.mock/i/otto/a922e336-b5bf-5411-97b9-be0f9c458e44",
        ],
        price=799.99,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=7311271700685,
        asin=None,
    )

    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
