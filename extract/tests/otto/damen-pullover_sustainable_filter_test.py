from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import ConsumerLifestageType, CountryType, GenderType

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore
from extract.extractors.otto_de import SUSTAINABILITY_FILTER
from tests.utils import read_test_html


def test_otto_basic() -> None:
    url = "https://www.otto.mock/"
    timestamp = "2022-02-17 12:49:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "damen-pullover.html"
    category = "SWEATER"
    gender = GenderType.FEMALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    original_URL = f"{url}{SUSTAINABILITY_FILTER}"
    meta_information = {"family": "FASHION", "original_URL": original_URL}

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

    assert actual is None
