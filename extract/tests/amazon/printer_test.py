from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_electronics() -> None:
    timestamp = "2022-04-28 19:00:00"
    url = "https://www.amazon.de/Kyocera-Klimaschutz-System-Ecosys-P3145dn-Laserdrucker/dp/B07TXRHFYS/ref=sr_1_23?qid=1651401368&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1-23&th=1%22"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "printer.html"
    category = "PRINTER"
    meta_information = {
        "family": "electronics",
        "price": "599,00",
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
        name="Kyocera Klimaschutz-System Ecosys P3145dn Laserdrucker: Schwarz-Weiß, "
        "Duplex-Einheit, 45 Seiten pro Minute. Inkl. Mobile Print Funktion",
        description="Geben Sie Ihr Modell ein, um sicherzustellen, dass dieser Artikel passt.. "
        "Zuverlässig: Der professionelle Ecosys Schwarz-Weiß Bürodrucker druckt bis zu 45 A4 "
        "Seiten/Minute und ist ideal für den Einsatz in Büroumgebungen wie (Home)Office, "
        "Praxis oder Kanzlei. Umweltfreundlich: Klimaschutz-System = klimafreundlich drucken "
        "und kopieren. Weitere Infos zur Kyocera Klimaschutz Initiative finden Sie unter dem "
        "Suchbegriff printgreen bei Kyocera in Ihrem Browser. Leistungsstark: Der Profi-"
        "Netzwerkdrucker mit doppelseitigem Druck, 600 Blatt Standard Papierkapazität, USB "
        "und Gigabit LAN druckt effizient und geräuscharm mit der Funktion Leiser Druck. "
        "Langlebigkeit: Der Laser-Drucker ist aus hochwertigen Materialien mit einer extrem "
        "hohen Lebensdauer gefertigt und ist speziell für den Einsatz in Geschäftsumgebungen "
        "geeignet und konzipiert. Sicherheit: Umfangreiche, integrierte Sicherheitsfunktionen "
        "für Unternehmensnetzwerke durch SSL, IPsec und Vertraulichen Druck",
        brand="Kyocera",
        sustainability_labels=[CertificateType.BLUE_ANGEL_PRINTER],  # type: ignore[attr-defined]
        price=599.00,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/I/41UAg0LchaL.jpg",
            "https://m.media-amazon.com/images/I/41ybCjXFRkL.jpg",
        ],
        colors=["Grau"],
        sizes=[
            "45 Seiten pro Minute",
            "50 Seiten pro Minute",
            "55 Seiten pro Minute",
            "60 Seiten pro Minute",
            "2 Jahre Herstellergarantie",
            "3 Jahre vor Ort Herstellergarantie",
        ],
        gtin=None,
        asin="B07TXRHFYS",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
