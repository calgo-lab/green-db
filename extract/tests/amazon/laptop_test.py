from core.constants import TABLE_NAME_SCRAPING_AMAZON
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_amazon_electronics() -> None:
    timestamp = "2022-04-28 19:00:00"
    url = "https://www.amazon.de/Lenovo-ThinkPad-i7-1160G7-Graphics-Windows/dp/B08WC37LYB/ref=sr_1_12?qid=1651408666&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1https://www.amazon.de/Lenovo-ThinkPad-i7-1160G7-Graphics-Windows/dp/B08WC37LYB/ref=sr_1_12?qid=1651408666&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1-12&th=1-12&th=1"  # noqa
    merchant = "amazon"
    file_name = "laptop.html"
    category = "LAPTOP"
    meta_information = {"family": "electronics", "price": "2998,0"}

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_AMAZON, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="Lenovo ThinkPad X1 Nano - Laptop Black 16GB RAM 1TB SSD",
        description="Lenovo ThinkPad X1 Nano Gen 1 Notebook 33 cm (13 Zoll), 2K "
        "(Intel Core i7-1160G7, 16 GB RAM, 1 TB SSD, Intel Iris Xe Graphics, Windows 10 Pro), "
        "Schwarz spanische QWERTY-Tastatur",
        brand="Lenovo",
        sustainability_labels=["certificate:EPEAT"],
        price=2998.0,
        currency="EUR",
        image_urls=[
            "https://m.media-amazon.com/images/I/41q5QmxMFYL.jpg",
            "https://m.media-amazon.com/images/I/41ii1ViuGuL.jpg",
            "https://m.media-amazon.com/images/I/31LC85nNfZL.jpg",
            "https://m.media-amazon.com/images/I/41h5YqQqEdL.jpg",
            "https://m.media-amazon.com/images/I/316v2VeOxwL.jpg",
            "https://m.media-amazon.com/images/I/21FGojgZvcL.jpg",
            "https://m.media-amazon.com/images/I/21DU9eh-mHL.jpg",
        ],
        color="Black",
        size=None,
        gtin=None,
        asin="B08WC37LYB",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
