from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_OTTO_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_otto_basic() -> None:
    # original url: https://www.otto.de/p/samsung-side-by-side-rs6ga884csl-178-cm-hoch-91-2-cm-breit-1524534276/#variationId=1524535294 # noqa
    url = "https://www.otto.mock/"
    timestamp = "2022-05-31 10:45:00"
    source = "otto"
    merchant = "otto"
    country = CountryType.DE
    file_name = "electronics-fridge.html"
    category = "FRIDGE"
    meta_information = {"family": "electronics"}

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
        name="Samsung Side-by-Side RS6GA884CSL, 178 cm hoch, 91,2 cm breit",
        description="Der »RS6GA884CSL« ist ein freistehender Side-by-Side Kühlschrank von Samsung "
        "und überzeugt mit hoher Funktionalität sowie der "
        "Energieeffizienz-Klassifizierung C (Skala Energieeffizienz-Klassifizierung "
        "Einheitsskala (A bis G)). Die Maße des Side-by-Side Kühlschranks kommen auf "
        "91,2 x 178 x 73,5 cm (B/H/T). Die Bildung von Eiskristallen wird durch die "
        "No Frost-Funktion verhindert – so muss das Gerät nie wieder abgetaut werden. "
        "Es sind zwei Gefrierschubladen und vier Gemüseschubladen zum Verstauen des "
        "Einkaufs integriert. Das innen installierte Display zeigt die genaue "
        "Temperatur im Gerät an. Die fünf Ablageflächen bieten viel Platz für "
        "Lebensmittel. Schnell griffbereit sind Lebensmittel in den fünf Türablagen. "
        "Bei offen stehender Tür meldet dies der Side-by-Side Kühlschrank mit einem "
        "Warnsignal. Dank der LED-Innenbeleuchtung findet man ganz problemlos, "
        "was man sucht. Der »RS6GA884CSL« von Samsung ist ein Side-by-Side "
        "Kühlschrank, der mit seinen Features überzeugt und ausreichend Platz für "
        "Lebensmittel aller Art bietet.",
        brand="Samsung",
        sustainability_labels=[CertificateType.EU_ENERGY_LABEL_C, CertificateType.OTHER],  # type: ignore[attr-defined] # noqa
        image_urls=[
            "https://i.otto.mock/i/otto/02f85090-393a-5bd1-b56a-bac9f66295f7",
            "https://i.otto.mock/i/otto/e1f3b715-0081-5df1-9d50-14c19bc476e8",
            "https://i.otto.mock/i/otto/5d309975-6917-5f9e-b206-a1c99e83411c",
        ],
        price=2189.00,
        currency=CurrencyType.EUR,
        colors=None,
        sizes=None,
        gtin=8806092536593,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
