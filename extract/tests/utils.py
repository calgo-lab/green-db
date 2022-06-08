from datetime import datetime
from pathlib import Path

from core.domain import PageType, ScrapedPage

TEST_DATA_DIR = Path(__file__).parent


def read_test_html(
    timestamp: str,
    merchant: str,
    country_code: str,
    file_name: str,
    category: str,
    meta_information: dict,
    url: str = "dummy_url",
) -> ScrapedPage:
    path = TEST_DATA_DIR / merchant / "data" / file_name
    with open(path, encoding="utf-8") as f:
        return ScrapedPage(
            timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
            merchant=merchant,
            country_code=country_code,
            url=url,
            html=f.read(),
            category=category,
            page_type=PageType("PRODUCT"),
            meta_information=meta_information,
        )
