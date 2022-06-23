from core.constants import TABLE_NAME_SCRAPING_HM_FR
from core.domain import Product
from extract import extract_product

from ..utils import read_test_html


def test_hm_basic() -> None:
    timestamp = "2022-06-06 11:21:00"
    url = "https://www2.hm.com/fr_fr/productpage.1045436003.html"
    merchant = "hm"
    country = "FR"
    file_name = "male-pant-wrong-encoding.html"
    category = "PANT"
    meta_information = {
        "family": "FASHION",
        "sex": "MALE",
    }

    scraped_page = read_test_html(
        timestamp=timestamp,
        merchant=merchant,
        country=country,
        file_name=file_name,
        category=category,
        meta_information=meta_information,
        url=url,
    )
    actual = extract_product(TABLE_NAME_SCRAPING_HM_FR, scraped_page)
    expected = Product(
        timestamp=timestamp,
        url=url,
        merchant=merchant,
        country=country,
        category=category,
        name="Short en jean Hybrid Regular",
        description="Pantalon jogger 5 poches en denim extensible de coton mélangé. Modèle avec "
        "taille de hauteur classique soulignée par lien de serrage dissimulé devant "
        "et élastique habillé dans le dos. Braguette zippée surmontée d’un bouton. "
        "Jambes droites pour une bonne aisance de mouvement au niveau des cuisses et "
        "des genoux. Article bénéficiant de la technologie Lycra® Hybrid qui apporte "
        "une souplesse et un confort exceptionnels, sans pour autant renoncer à un "
        "aspect denim authentique.",
        brand="H&M",
        sustainability_labels=[
            "certificate:HM_CONSCIOUS",
            "certificate:OTHER",
        ],
        price=29.99,
        currency="EUR",
        image_urls=[
            "https://lp2.hm.com/hmgoepprod?set=quality%5B79%5D%2Csource%5B%2Fdd%2F3e"
            "%2Fdd3e47e1d6c7285c0a2e6ad00a79d577757e1330.jpg%5D%2Corigin%5Bdam%5D%2Ccategory%5B"
            "%5D%2Ctype%5BDESCRIPTIVESTILLLIFE%5D%2Cres%5Bm%5D%2Chmver%5B2%5D&call=url["
            "file:/product/main]",
        ],
        color=["Noir"],
        size=["28", "29", "30", "31", "32", "33", "34", "36", "38", "40", "42", "28S", "29S", "30S",
              "31S", "32S", "33S", "34S", "36S"],
        gtin=None,
        asin=None,
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
