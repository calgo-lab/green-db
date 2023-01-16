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
            <div class='prd_sustainabilityLayer__caption'> Unterstützt Cotton made in Africa </div>
            <div class='prd_sustainabilityLayer__description'> some description </div>
            <div class='prd_sustainabilityLayer__licenseNumber'> some license </div>
        </div>
    """
    requests_mock.register_uri("GET", "/product/sustainability/layerContent", text=label_html)

    # original_url: https://www.otto.de/p/h-i-s-rundhalsshirt-packung-3-tlg-3er-pack-mit-druck-1379261103/#variationId=1379261260 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-04-19 12:49:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "herren-shirt.html"
    category = "SHIRT"
    gender = GenderType.MALE
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
        name="H.I.S Rundhalsshirt (Packung, 3-tlg., 3er-Pack) mit Druck",
        description="Hier kommt dein neues Lieblingsshirt Schau dir das Rundhalsshirt von H.I.S "
                    "mal genauer an. Durch den Aufdruck wirkt es sowohl locker als auch frisch. "
                    "Dieses Shirt ist schmal geschnitten, sodass dein Oberkörper dezent zur "
                    "Geltung gebracht wird. Der Single Jerseystoff aus Baumwolle ist angenehm "
                    "weich auf der Haut und sorgt für hohen Tragekomfort. Starkes "
                    "Kombinationstalent Eine trendige Freizeitkombination hast du mit Jeans und "
                    "bunten Sneakern. Unter einem Sakko getragen, wird der Look schick - und sehr "
                    "stylisch, wenn die Farben beider Teile aufeinander abgestimmt sind. Das "
                    "Shirt ist im 3er-Pack erhältlich. Dein neues Shirt von H.I.S ist die "
                    "Grundlage für einen trendigen Look.",
        brand="H.I.S",
        sustainability_labels=[CertificateType.COTTON_MADE_IN_AFRICA],  # type: ignore[attr-defined]
        image_urls=[
            "https://i.otto.mock/i/otto/05cb3291-9921-5253-85d0-1e97c3dd5b37",
            "https://i.otto.mock/i/otto/77656fe2-ac3f-5242-9bb0-61b5d2f768a6",
            "https://i.otto.mock/i/otto/7072f590-6798-549a-bf2d-e8e82c6a6ed5",
        ],
        price=29.99,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=8907890476446,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
