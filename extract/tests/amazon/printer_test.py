from core.constants import TABLE_NAME_SCRAPING_AMAZON
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_amazon_electronics() -> None:
    timestamp = "2022-04-28 19:00:00"
    url = "https://www.amazon.de/Kyocera-Klimaschutz-System-Ecosys-P3145dn-Laserdrucker/dp/B07TXRHFYS/ref=sr_1_23?qid=1651401368&refinements=p_n_cpf_eligible%3A22579885031&s=computers&sr=1-23&th=1%22"  # noqa
    merchant = "amazon"
    file_name = "printer.html"
    category = "PRINTER"
    meta_information = {
        "family": "electronics",
        "sex": "MALE",
        "price": "599,00",
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
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
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
        sustainability_labels=["certificate:BLUE_ANGEL"],
        price=599.00,
        currency="EUR",
        image_urls=[
            "https://m.media-amazon.com/images/I/41UAg0LchaL._AC_US40_.jpg",
            "https://m.media-amazon.com/images/I/41ybCjXFRkL._AC_US40_.jpg",
        ],
        color="Grau",
        size="45 Seiten pro Minute, 50 Seiten pro Minute, 55 Seiten pro Minute, 60 Seiten pro Minute, 2 Jahre Herstellergarantie, 3 Jahre vor Ort Herstellergarantie",
        gtin=None,
        asin="B07TXRHFYS",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
