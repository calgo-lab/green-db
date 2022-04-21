from core.constants import TABLE_NAME_SCRAPING_AMAZON
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_amazon_basic() -> None:
    timestamp = "2022-04-21 19:00:00"
    url = "https://www.amazon.de/-/en/Kong_3-000284-Chrome-Free-Sustainable-Interchangeable-Footbed/dp/B08FRFD62N/ref=sr_1_1?qid=1650559557&refinements=p_n_cpf_eligible%3A22579885031&s=shoes&sr=1-1&th=1"  # noqa
    merchant = "amazon"
    file_name = "shoes.html"
    category = "SHOES"
    meta_information = {
        "family": "FASHION",
        "sex": "MEN",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_AMAZON, scraped_page)
    expected = Product() # TODO
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
