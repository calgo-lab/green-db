from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_otto_basic() -> None:
    # original url: https://www.otto.de/p/sony-xperia-1-iii-5g-256gb-smartphone-16-51-cm-6-5-zoll-256-gb-speicherplatz-12-mp-kamera-C1397609879/#variationId=1397609888 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "electronics-phone-nonsustainable.html"
    category = "SMARTPHONE"
    meta_information = {"family": "electronics", "original_URL": url}

    scraped_page = read_test_html(
        timestamp=timestamp,
        source=source,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url
    )

    actual = extract_product(TABLE_NAME_SCRAPING_OTTO_DE, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        source=source,
        merchant=merchant,
        country=country,
        category=category,
        gender=None,
        consumer_lifestage=None,
        name="Sony Xperia 1 III 5G, 256GB Smartphone (16,51 cm/6,5 Zoll, 256 GB Speicherplatz, "
        "12 MP Kamera)",
        description="Smartphone Das Sony Xperia 1 III 5G, 256GB mit 6,5 Zoll Display ist dein "
        "Begleiter in allen Lebenssituationen, egal ob zum Surfen, Chatten, "
        "Fotografieren oder Spielen. Dieses Modell hat 2 SIM-Karten-Steckplätze. So "
        "kannst du zum Beispiel unterschiedliche Tarife effizient verbinden. Große "
        "Datenmengen – wie Spiele, Fotos und Videos – finden auf dem 256 GB großen "
        "Speicher genug Platz. Du suchst ein Smartphone mit besonders großem Display? "
        "Dann könnte dieses Modell das richtige sein. Impressionen auf "
        "Ultra-HD-Videos festhalten Auf der Rückseite des Smartphones befindet sich "
        "eine 12-Megapixel-Hauptkamera. 8 Megapixel bieten die 2 Frontkameras. Zwei "
        "Frontkameras bringen umfangreichere Aufnahmefunktionen und eine höhere "
        "Qualität der Fotos mit sich. Das Gerät nimmt Videos in hochauflösender "
        "Ultra-HD-Qualität auf– diese können somit ohne Probleme auch auf einem "
        "größeren Bildschirm gezeigt werden. Für Apps und Co. einen extra großen "
        "Speicher Der integrierte Datenspeicher hat ein beachtlich großes Volumen von "
        "256 GB. Du hast also Platz für sehr viele Fotos, Videos, Musik und "
        "Anwendungen – so stehst du nie vor dem Problem, zu wenig Speicherplatz zu "
        "haben. Display mit Gorilla-Glas Im Vergleich zu normalem Glas ist das hier "
        "eingesetzte Gorilla-Glas kratzfester, leichter und lichtdurchlässiger. "
        "Staub- und strahlwassergeschützt, um Schäden zu verhindern Damit das Gerät "
        "dir lange erhalten bleibt, ist es staub- und strahlwassergeschützt. Dadurch "
        "dass dieses Modell über 2 Slots für SIM-Karten verfügt, kannst du "
        "verschiedene Mobilfunkverträge in einem Gerät verwenden. Googles "
        "Sprachassistent lässt sich auf dem Sony Xperia 1 III 5G, 256GB nutzen und "
        "gibt dir die Möglichkeit, dieses schnell und bequem zu bedienen.",
        brand="Sony",
        sustainability_labels=[CertificateType.UNAVAILABLE],  # type: ignore[attr-defined] # noqa
        image_urls=[
            "https://i.otto.mock/i/otto/eb2cc281-4f81-5c21-89ac-21235628df4a",
            "https://i.otto.mock/i/otto/f301b567-267d-5547-a4f1-27864f9cd864",
            "https://i.otto.mock/i/otto/a922e336-b5bf-5411-97b9-be0f9c458e44",
        ],
        price=799.99,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=7311271700685,
        asin=None,
    )

    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
