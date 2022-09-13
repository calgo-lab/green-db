from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import (
    CertificateType,
    ConsumerLifestageType,
    CountryType,
    CurrencyType,
    GenderType,
    Product,
)

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_basic() -> None:
    timestamp = "2022-08-25 20:21:00"
    url = "https://www.amazon.de/Think-Kong_3-000371-chromfrei-nachhaltige-Wechselfu%C3%9Fbett/dp/B08FSL34LS/ref=sr_1_2?qid=1651058159&refinements=p_n_cpf_eligible%3A22579885031&s=shoes&sr=1-2"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "shoes.html"
    category = "SHOES"
    gender = GenderType.MALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    meta_information = {
        "family": "FASHION",
        "price": "77,62",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        source=source,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        gender=gender,
        consumer_lifestage=consumer_lifestage,
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
        gender=gender,
        consumer_lifestage=consumer_lifestage,
        name="THINK! Herren Kong_3-000371 chromfrei gegerbte, nachhaltige Wechselfußbett Boots",
        description="Obermaterial: Leder. Innenmaterial: Lederfutter. Sohle: Gummi. Verschluss: "
        "Schnüren. Absatzhöhe: 2 cm. Absatzform: Blockabsatz. Größenhinweis: Bequeme "
        "Passform. Schuhweite: Normal. Nicht wasserfest. Think! ist ein "
        "traditionelles Schuhunternehmen und wahrt die Handwerkskunst. "
        "Think! Schuhe sind handgefertigt und werden ausschließlich in Europa hergestellt. "
        "Die Schuhe sind dabei individuell, gesund und nachhaltig produziert. Alle Innenleder "
        "sind chromfrei gegerbt. Durch die schonende, pflanzliche Gerbung entsteht ein angenehmes "
        "Klima im Schuh. Die beim Tragen entstehende Feuchtigkeit wird sofort aufgenommen und "
        "hält die Füße trocken. Die in vielen Modellen eingesetzten KorkEinlagen wirken "
        "antibakteriell. Die eingeschlossenen Luftkammern dämpfen jeden Schritt und lassen den "
        "Füßen genug Luft zum Atmen.Lässig, individuell und bequem sind die KONG Schnürer für "
        "Herren. Die asymmetrischen Schuhspitzen mit breiterem Vorderfußbereich sind anatomisch "
        "geformt und bieten den Zehen reichlich Platz. Die Latexsohle hat integrierte Luftkammern. "
        "Dadurch werden Stöße abgedämpft und der Fuß wird stabilisiert. Die Dämpfung schont die "
        "Gelenke und die Bänder. Das sorgt für weiches, federleichtes Gehvergnügen. Das markante "
        "Sohlenprofil bietet n Halt auf allen Oberflächen. KONG Modelle sind mit einem "
        "Wechselfußbett ausgestattet. Das bedeutet, dass die Einlegesohlen ganz leicht durch "
        "orthopädische Einlagen oder später durch neue KONG Einlagen ausgetauscht werden können. "
        "Einige KONG Modelle wurden mit dem Österreichischen Umweltzeichen ausgezeichnet.",
        brand="Think!",
        sustainability_labels=[CertificateType.BLUE_ANGEL],  # type: ignore[attr-defined]
        price=77.62,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/I/31qGkKiX4GL.jpg",
            "https://m.media-amazon.com/images/I/31CkE5Ya1IL.jpg",
            "https://m.media-amazon.com/images/I/318QiVbjdWL.jpg",
            "https://m.media-amazon.com/images/I/31i94PNyFTL.jpg",
            "https://m.media-amazon.com/images/I/31yzw7fkuKL.jpg",
            "https://m.media-amazon.com/images/I/31CvUUqMkRL.jpg",
            "https://m.media-amazon.com/images/I/31Gkl-CPiiL.jpg",
        ],
        colors=["3000 Cuoio Kombi"],
        sizes=[
            "40 EU",
            "40.5 EU",
            "41 EU",
            "41.5 EU",
            "42 EU",
            "42.5 EU",
            "43 EU",
            "43.5 EU",
            "44 EU",
            "44.5 EU",
            "45 EU",
            "45.5 EU",
            "46 EU",
            "46.5 EU",
            "47 EU",
            "47.5 EU",
        ],
        gtin=None,
        asin="B08FSZSW2L",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
