from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_electronics() -> None:
    timestamp = "2022-08-25 14:46:00"
    url = "https://www.amazon.de/-/en/Midea-Washing-Machine-5-840-Reload/dp/B092LGG221/ref=sr_1_1?c=ts&keywords=Haushalts-Gro%C3%9Fger%C3%A4te&qid=1661427776&refinements=p_n_cpf_eligible%3A22579885031&rnid=22579884031&s=kitchen&sr=1-1&ts_id=16075741&th=1"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "washer.html"
    category = "WASHER"
    meta_information = {
        "family": "household",
        "price": "379,00",
    }

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
    actual = extract_product(TABLE_NAME_SCRAPING_AMAZON_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=None,
        consumer_lifestage=None,
        name="Midea Washing Machine W 5.840 iN / 8 kg / Steam Care / Reload - Refill Function / "
        "BLDC Inverter Motor / 1400 rpm, White",
        description="Make sure this fits by entering your model number.. 8 kg capacity. Energy "
        "efficiency class B / BLDC inverter motor / 1400 revolutions per minute. "
        "Quick wash 15 inches / short wash 45 inches. Reload recall function, "
        "child lock, AquaStop. Steam care - While steam care helps to reduce bad "
        "odours and wrinkles, Allergy Care is the best solution to kill "
        "allergy-causing substances and mites and reduce skin irritation in sensitive "
        "people. Together, the two programs contribute to a more pleasant life.. "
        "Pre-wash - Additional wash cycle before starting the main wash to increase "
        "the washing performance.. Unit dimensions (H x W x D): 85 x 60 x 57 cm",
        brand="Midea",
        sustainability_labels=[CertificateType.EU_ENERGY_LABEL_B],  # type: ignore[attr-defined]
        price=379.00,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/I/31uH6SJs+XS.jpg",
            "https://m.media-amazon.com/images/I/411zsS-JW8S.jpg",
            "https://m.media-amazon.com/images/I/310FP7ymDqS.jpg",
            "https://m.media-amazon.com/images/I/31qC0k3oQoS.jpg",
            "https://m.media-amazon.com/images/I/31FqjB7v08S.jpg",
            "https://m.media-amazon.com/images/I/41W-4x1X7+L.jpg",
            "https://m.media-amazon.com/images/I/41Ww+CQnB+S.jpg",
        ],
        colors=["8 kg"],
        sizes=None,
        gtin=None,
        asin="B092LGG221",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
