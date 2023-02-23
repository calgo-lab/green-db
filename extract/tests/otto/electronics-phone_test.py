from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product
from extract import extract_product  # type: ignore


def test_otto_basic() -> None:
    # original url: https://www.otto.de/p/fairphone-fairphone-4-bundle-mit-recable-usb-c-kabel-plus-charger-smartphone-6-3-zoll-48-mp-kamera-S0S5O0LN/#variationId=S0S5O0LNJ6FV # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "electronics-smartphone.html"
    category = "SMARTPHONE"
    meta_information = {"family": "electronics", "original_URL": url}

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
        name="Fairphone Fairphone 4 Bundle mit recable USB-C Kabel + Charger Smartphone (6,3 Zoll, "
        "48 MP Kamera)",
        description="Leave short description",
        brand="Fairphone",
        sustainability_labels=[CertificateType.BLUE_ANGEL_SMARTPHONES, CertificateType.OTHER],  # type: ignore[attr-defined] # noqa
        image_urls=[
            "https://i.otto.mock/i/otto/34a45e3a-7b50-45fd-86b7-c10373a243b7",
            "https://i.otto.mock/i/otto/0ae22a98-b2fc-4015-a6b1-67bf6997219b",
            "https://i.otto.mock/i/otto/c6de4b64-bda1-4a8c-bcd2-331eba4e1fbf",
        ],
        price=619.9,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=4250851617896,
        asin=None,
    )

    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
