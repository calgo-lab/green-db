from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_electronics() -> None:
    timestamp = "2022-08-25 20:21:00"
    url = "https://www.amazon.de/Lenovo-ThinkPad-i7-1160G7-Graphics-Windows/dp/B08WC37LYB/ref=sr_1_12?qid=1651408666&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1https://www.amazon.de/Lenovo-ThinkPad-i7-1160G7-Graphics-Windows/dp/B08WC37LYB/ref=sr_1_12?qid=1651408666&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1-12&th=1-12&th=1"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "laptop.html"
    category = "LAPTOP"
    meta_information = {"family": "electronics", "price": "2998,0"}

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
        name="Lenovo ThinkPad X1 Nano - Laptop Black 16GB RAM 1TB SSD",
        description="Geben Sie Ihr Modell ein, um sicherzustellen, dass dieser Artikel passt.. "
        "Bildschirm 13 Zoll (33 cm), 2K, 2160 x 1350 Pixel, IPS, 450nits, blendfrei. "
        "Prozessor Intel Core i7-1160G7 (4C / 8T, 2,1 / 4,4 GHz, 12 MB). RAM 16 GB "
        "Soldered LPDDR4x-4266. Speicher: 1 TB SSD M.2 2242 PCIe 3.0x4 NVMe. "
        "Integrierte Grafikkarte Intel Iris Xe Graphics. Lenovo ThinkPad X1 Nano Gen "
        "1 Notebook 33 cm (13 Zoll), 2K (Intel Core i7-1160G7, 16 GB RAM, 1 TB SSD, "
        "Intel Iris Xe Graphics, Windows 10 Pro), Schwarz spanische QWERTY-Tastatur",
        brand="Lenovo",
        sustainability_labels=[CertificateType.EPEAT],  # type: ignore[attr-defined]
        price=2998.0,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/I/41q5QmxMFYL.jpg",
            "https://m.media-amazon.com/images/I/41ii1ViuGuL.jpg",
            "https://m.media-amazon.com/images/I/31LC85nNfZL.jpg",
            "https://m.media-amazon.com/images/I/41h5YqQqEdL.jpg",
            "https://m.media-amazon.com/images/I/316v2VeOxwL.jpg",
            "https://m.media-amazon.com/images/I/21FGojgZvcL.jpg",
            "https://m.media-amazon.com/images/I/21DU9eh-mHL.jpg",
        ],
        colors=["Black"],
        sizes=None,
        gtin=None,
        asin="B08WC37LYB",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
