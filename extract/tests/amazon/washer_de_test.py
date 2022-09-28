from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_electronics() -> None:
    timestamp = "2022-08-25 14:46:00"
    url = "https://www.amazon.de/Candy-RO-1486DWMCE-1-S-Waschmaschine/dp/B08R3YHPK1/ref=sr_1_121?qid=1663982677&refinements=p_n_cpf_eligible%3A22579885031&s=appliances&sr=1-121"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "washer_de.html"
    category = "WASHER"
    meta_information = {
        "family": "household",
        "price": "477,69",
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
        name="Candy RapidÓ RO 1486DWMCE/1-S Waschmaschine / 8 kg/Smarte Bedienung mit Wi-Fi + "
        "Bluetooth/Easy Iron - Dampffunktion, Weiß",
        description="Geben Sie Ihr Modell ein, um sicherzustellen, dass dieser Artikel passt.. "
        "Installation type: Freistehend. Nützliches Produkt mit hoher Qualität. Candy "
        "RapidÓ RO 1486DWMCE/1-S Waschmaschine / 8 kg / Smarte Bedienung mit Wi-Fi + "
        "Bluetooth / Easy Iron - Dampffunktion Candy RapidÓ RO 1486DWMCE/1-S "
        "Waschmaschine / 8 kg/Smarte Bedienung mit Wi-Fi + Bluetooth/Easy Iron - "
        "Dampffunktion Weiß",
        brand="Candy",
        sustainability_labels=[CertificateType.EU_ENERGY_LABEL_A],  # type: ignore[attr-defined]
        price=477.69,
        currency=CurrencyType.EUR,
        image_urls=["https://m.media-amazon.com/images/I/31Fr9GUdkhL.jpg"],
        colors=["Weiß"],
        sizes=None,
        gtin=None,
        asin="B08R3YHPK1",
    )
    for attribute in expected.__dict__.keys():

        assert actual.__dict__[attribute] == expected.__dict__[attribute]
