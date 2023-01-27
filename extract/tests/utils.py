from datetime import datetime
from pathlib import Path
from typing import Optional

from core.domain import ConsumerLifestageType, CountryType, GenderType, PageType, ScrapedPage


def read_test_html(
    timestamp: str,
    source: str,
    merchant: str,
    country: CountryType,
    file_name: str,
    category: str,
    meta_information: dict,
    url: str = "dummy_url",
    gender: Optional[GenderType] = None,
    consumer_lifestage: Optional[ConsumerLifestageType] = None
) -> ScrapedPage:
    path = TEST_DATA_DIR / merchant / "data" / file_name
    with open(path, encoding="utf-8") as f:
        return ScrapedPage(
            timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
            source=source,
            merchant=merchant,
            country=country,
            url=url,
            html=f.read(),
            category=category,
            gender=gender,
            consumer_lifestage=consumer_lifestage,
            page_type=PageType("PRODUCT"),
            meta_information=meta_information
        )


TEST_DATA_DIR = Path(__file__).parent
