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


def test_otto_basic() -> None:
    # original url: https://www.otto.de/p/casual-looks-rundhalsshirt-shirt-645503675/#variationId=144423297 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-09-28 15:14:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "damen-shirt.html"
    category = "SHIRT"
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
        name="Casual Looks Rundhalsshirt »Shirt« (1-tlg)",
        description="Shirt mit Rundhals-Ausschnitt – ein echtes Basic für Ihre Garderobe! 100% "
                    "Baumwolle. Maschinenwäsche.",
        brand="Casual Looks",
        sustainability_labels=[CertificateType.COTTON_MADE_IN_AFRICA],  # type: ignore[attr-defined]
        image_urls=[
            "https://i.otto.mock/i/otto/4c506363-076b-56e8-9521-ca9467f81d6c",
            "https://i.otto.mock/i/otto/df4d1d25-0e9f-5f68-9a7b-8596e65dab30",
        ],
        price=12.99,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=5205012107630,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
