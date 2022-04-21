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
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="Think! Herren Kong_3-000284 Chromfrei Gegerbte, Nachhaltige Wechselfußbett Schnürhalbschuhe",
        description=" Think! ist ein traditionelles Schuhunternehmen und wahrt die Handwerkskunst. Think! Schuhe sind handgefertigt und werden ausschließlich in Europa hergestellt. Die Schuhe sind dabei individuell, gesund und nachhaltig produziert. Alle Innenleder sind chromfrei gegerbt. Durch die schonende, pflanzliche Gerbung entsteht ein angenehmes Klima im Schuh. Die beim Tragen entstehende Feuchtigkeit wird sofort aufgenommen und hält die Füße trocken. Die in vielen Modellen eingesetzten KorkEinlagen wirken antibakteriell. Die eingeschlossenen Luftkammern dämpfen jeden Schritt und lassen den Füßen genug Luft zum Atmen.Lässig, individuell und bequem sind die KONG Schnürer für Herren. Die asymmetrischen Schuhspitzen mit breiterem Vorderfußbereich sind anatomisch geformt und bieten den Zehen reichlich Platz. Die Latexsohle hat integrierte Luftkammern. Dadurch werden Stöße abgedämpft und der Fuß wird stabilisiert. Die Dämpfung schont die Gelenke und die Bänder. Das sorgt für weiches, federleichtes Gehvergnügen. Das markante Sohlenprofil bietet n Halt auf allen Oberflächen. KONG Modelle sind mit einem Wechselfußbett ausgestattet. Das bedeutet, dass die Einlegesohlen ganz leicht durch orthopädische Einlagen oder später durch neue KONG Einlagen ausgetauscht werden können. Einige KONG Modelle wurden mit dem Österreichischen Umweltzeichen ausgezeichnet.  ",
        brand="THINK!",
        sustainability_labels=["certificate:BLUE_ANGEL"],
        price=69.80,
        currency="EUR",
        image_urls=[],
        color="0000 Black",
        size=None,
        gtin=None,
        asin="B09BFC4BN8",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
