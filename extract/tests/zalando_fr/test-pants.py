from core.constants import TABLE_NAME_SCRAPING_ZALANDO_FR
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_zalando_basic() -> None:
    timestamp = "2022-04-12 12:31:50"
    url = "https://www.zalando.mock/"
    merchant = "zalando_fr"
    file_name = "pants.html"
    category = "PANT"
    meta_information = {"family": "FASHION", "sustainability": "water_saving", "sex": "FEMALE"}

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_ZALANDO_FR, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        category=category,
        name="Pantalon classique - marine",
        description="Commander hessnatur Pantalon classique - marine  à 159,95\xa0€ le 2022-04-06 sur Zalando. Livraison gratuite à partir de 24,90€.",  # noqa
        brand="hessnatur",
        sustainability_labels=["certificate:OTHER"],
        price=159.95,
        currency="EUR",
        image_urls=[
            "https://img01.ztat.net/article/spp-media-p1/06b423a888294f4dbbb8efa96e468457/5507c3b658844293828db28c2e30ba08.jpg?imwidth=103",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/7267552eb1784d1b97dd69e1eacb5c97/05e940cac34241c098fd4b4c9c705a0a.jpg?imwidth=103",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/e73e884e97cd483e83ac30929d27dfbc/3066467a32b64e1f80864138fd1652f1.jpg?imwidth=103",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/4f7262849bfd4d35af13c4203123f7dd/94f14748171145f88c353567b4fbe1f3.jpg?imwidth=103",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/21af7a8db6d54cc8b83f14b532a2e22a/c873800ac74c4f219329b2fb0df7295d.jpg?imwidth=103",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/326cc8c44327474ba483fb36e1b1e9a9/a09afe95b16d4feeb5814a2317d10ffc.jpg?imwidth=103&filter=packshot",  # noqa
            "https://img01.ztat.net/article/spp-media-p1/e28650c36c214e769df655e8def4566c/32e07b4688aa4e4ea92e9bd8273d13bb.jpg?imwidth=103",  # noqa
        ],
        color="marine/bleu",
        size=None,
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
