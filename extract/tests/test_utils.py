from pathlib import Path
from datetime import datetime

from core.domain import ScrapedPage
from core.domain import PageType

TEST_DATA_DIR = Path(__file__).parent


def read_test_html(
    timestamp: datetime, merchant: str, file_name: str, category: str, meta_information: dict, url: str = "dummy_url",
) -> ScrapedPage:
    path = TEST_DATA_DIR / merchant / file_name
    with open(path) as f:
        return ScrapedPage(
            timestamp=timestamp,
            merchant=merchant,
            url=url,
            html=f.read(),
            category=category,
            page_type=PageType("PRODUCT"),
            meta_information=meta_information,
        )
