from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import (
    CertificateType,
    ConsumerLifestageType,
    CountryType,
    CurrencyType,
    GenderType,
    Product,
)
from extract import extract_product

from ..utils import read_test_html


def test_amazon_basic_img() -> None:
    timestamp = "2022-04-28 19:00:00"
    url = "https://www.amazon.de/Romberg-Boxershorts-Bio-Baumwolle-kratzenden-nachhaltig/dp/B0932XK47G/ref=sr_1_7?qid=1652774791&refinements=p_n_cpf_eligible%3A22579885031&s=apparel&sr=1-7&th=1"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "underwear.html"
    category = "UNDERWEAR"
    gender = GenderType.MALE
    consumer_lifestage = ConsumerLifestageType.ADULT
    meta_information = {
        "family": "FASHION",
        "price": "49,95",
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
        name="Romberg Herren Boxershorts mit Schriftzug, 6er Pack aus nachhaltiger Bio-Baumwolle "
        "(GOTS Zertifiziert)",
        description="BIO-BAUMWOLLE: Du willst den Unterschied machen? Entscheide Dich bewusst für "
        "unsere Boxershorts aus nachhaltig angebauter Bio-Baumwolle, wenn Dir wichtig "
        "ist, dass ökologische, soziale und arbeitsrechtliche Bedingungen bei der "
        "Bekleidungsherstellung entlang der Lieferkette transparent sind und strikt "
        "eingehalten werden.. PERFEKTE PASSFORM UND BESTER TRAGEKOMFORT: Durch das "
        "weich ummantelte, dehnbare Gummibund und die elastische Baumwollware passt "
        "sich unsere Romberg Boxershorts optimal Deiner Figur an und engt nicht ein.. "
        "95% Baumwolle aus Kontrolliertem Biologischen Anbau, 5% Elasthan. "
        "Pflegehinweis: Waschen bei 60°C, Bügeln ohne Probleme möglich. GARANTIERTE "
        "HALTBARKEIT: Durch unsere hochwertige Nahtverarbeitung sind alle Nähte auf "
        "der Innenseite wunderbar weich und lange haltbar. Das garantieren wir. Und "
        "damit die Schrittnaht Deiner Boxershorts nicht ständig durch Reibung Deiner "
        "Jeans kaputt geht und auch noch kratzt, haben wir den Schnitt optimiert.. "
        "OPTIMALE HOSENBEINLÄNGE: Du kennst das Gefühl zu kurzer oder langer "
        "Hosenbeine bei Deiner Boxershorts, die verrutschen oder sich aufrollen? Dann "
        "entscheide Dich für unsere Romberg Boxershorts, die genau die richtige "
        "Beinlänge für Dich hat.. PRINT LABEL: Kratzende Etiketten nerven und sind "
        "ein absolutes No-Go! Deswegen haben wir das Etikett auf die Innenseite der "
        "Boxershorts gedruckt. So musst Du nie wieder lästige Etiketten aus Deiner "
        "Unterwäsche herausschneiden.",
        brand="Romberg",
        sustainability_labels=[CertificateType.GOTS_MADE_WITH_ORGANIC_MATERIALS],  # type: ignore[attr-defined]
        price=49.95,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/I/41b6Pwz5lrL.jpg",
            "https://m.media-amazon.com/images/I/41ySTdJA8AL.jpg",
            "https://m.media-amazon.com/images/I/41yh+a-ZwQL.jpg",
            "https://m.media-amazon.com/images/I/41tcQ6C1riL.jpg",
            "https://m.media-amazon.com/images/I/41bk5vXFDSL.jpg",
            "https://m.media-amazon.com/images/I/41xkOVB1dML.jpg",
            "https://m.media-amazon.com/images/I/41F+QWQPJ7L.jpg",
        ],
        colors=["Navy mit Schriftzug"],
        sizes=["S", "M", "L", "XL", "XXL", "3XL"],
        gtin=None,
        asin="B089658KBB",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
