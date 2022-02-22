from pathlib import Path

# from green_db_integration.domain import Page
from core.domain import ScrapedPage
from core.domain import PageType

TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test-data"


def read_test_html(merchant: str, file_name: str, category: str, url: str = "dummy_url") -> ScrapedPage:
    path = TEST_DATA_DIR / merchant / file_name
    with open(path) as f:
        return ScrapedPage(
            html=f.read(),
            merchant=merchant,
            category=category,
            url=url,
            page_type=PageType("PRODUCT"),
        )
