from tests.utils import read_test_html

from core.constants import TABLE_NAME_SCRAPING_AMAZON_DE
from core.domain import CertificateType, CountryType, CurrencyType, Product

# TODO: This is a false positive of mypy
from extract import extract_product  # type: ignore


def test_amazon_electronics() -> None:
    timestamp = "2022-08-25 22:21:00"
    url = "https://www.amazon.fr/HP-Chromebook-12b-ca0000sf-Ultraportable-Convertible/dp/B08RJGPSK6/ref=sr_1_8?qid=1656699722&refinements=p_n_cpf_eligible%3A22579881031&s=computers&sr=1-8"  # noqa
    source = "amazon"
    merchant = "amazon"
    country = CountryType.DE
    file_name = "chromebook-indice-fr.html"
    category = "LAPTOP"
    meta_information = {"family": "electronics", "price": "209,0"}

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
        name="HP Chromebook x360 12b-ca0000sf Ordinateur Ultraportable Convertible et Tactile "
        '12" HD (Intel Celeron, RAM 4 Go, eMMC 32 Go, AZERTY, ChromeOS)',
        description="Cliquez-ici pour vous assurer de la compatibilité de ce produit avec votre "
        "modèle. Système d'exploitation ChromeOS : démarrage en quelques secondes, "
        "reste rapide dans le temps grâce aux mises à jour automatiques, antivirus "
        "déjà intégré et batterie longue durée.. Profitez de milliers d'apps sur le "
        "Play Store ou sur le Web pour travailler, créer, regarder vos films/séries, "
        "jouer, et plus encore. Les Chromebooks sont compatibles avec Microsoft "
        "Office. Retrouvez les applis Word, Excel et PowerPoint sur le web.. "
        "Convertible : travaillez en position ordinateur portable, regardez des "
        "vidéos en position tente, et déplacez-vous en position tablette.. Ecran : "
        '12" HD | Processeur : Intel Celeron N4020. RAM : 4 Go | Stockage : 32 Go '
        "EMMC. Profitez de 100 Go de stockage en ligne offerts en activant l'offre "
        "d'essai d'1 an à Google One. Vos fichiers sont automatiquement sauvegardés, "
        "vous pouvez y accéder depuis n'importe quel device connecté à internet.. "
        "Autonomie : jusqu'à 13h. Faites-en plus avec une seule charge, Chrome OS "
        "optimise en permanence les performances de la batterie. | Poids : 1,"
        "35 kg. Connectivité : 1 x USB 3.1, 2 x USB Type C, lecteur de carte microSD, "
        "combo jack audio/micro. Cet ordinateur portable ne fonctionne pas sous le "
        "système d’exploitation Windows. Les Chromebooks sont des ordinateurs "
        "portables sûrs, rapides et intelligents qui fonctionnent sous le système "
        "d'exploitation Chrome OS : démarrage en quelques secondes, "
        "aucuns ralentissements dans le temps grâce aux mises à jour automatiques, "
        "antivirus déjà intégré et batterie longue durée.Que ce soit sur le Web ou "
        "via les applications du Google Play Store, vous pouvez tout faire avec les "
        "Chromebooks : laisser libre cours à votre créativité, optimiser votre "
        "productivité, regarder des films/séries ou jouer aux jeux que vous aimez "
        "déjà. Les Chromebooks sont compatibles avec Microsoft Word, Excel et "
        "PowerPoint.Profitez de 100 Go de stockage en ligne offerts en activant "
        "l'offre d'essai d'1 an à Google One. Vos fichiers sont automatiquement "
        "sauvegardés, vous pouvez y accéder depuis n'importe quel device connecté à "
        'internet.Découvrez le Chromebook HP x360 12b-ca0010nf et son écran 12" HD '
        "tactile et convertible en tablette. Travaillez en position ordinateur "
        "portable, regardez des vidéos en position tente, et déplacez-vous en "
        "position tablette. Processeur : Intel Celeron N4020 Mémoire RAM : 4 Go "
        "Stockage : 32 Go EMMC. Autonomie : jusqu'à 13h. Faites-en plus avec une "
        "seule charge, Chrome OS optimise en permanence les performances de la "
        "batterie. Poids : 1,35 kg Connectivité : 1 x USB 3.1, 2 x USB Type C, "
        "lecteur de carte microSD, combo jack audio/microPortable. Polyvalent. "
        "Applications pour tous les jours. Vous avez besoin de plus parce que vous "
        "faites plus.",
        brand="HP",
        sustainability_labels=[CertificateType.EPEAT_LAPTOPS, CertificateType["FR_REPAIR_INDEX_4-5.9"]],  # type: ignore[attr-defined] # noqa
        price=209.0,
        currency=CurrencyType.EUR,
        image_urls=[
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/41WhGbMlmQL.jpg",
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/412c4N3ID+L.jpg",
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/41-7IydJreL.jpg",
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/21jMFEcqlYL.jpg",
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/41W1Cdu-zXL.jpg",
            "https://m.media-amazon.com/images/W/WEBP_402378-T2/images/I/41K1Yxt3tiL.jpg",
        ],
        colors=['12"'],
        sizes=None,
        gtin=None,
        asin="B08RJGPSK6",
    )
    for attribute in expected.__dict__.keys():
        assert actual.__dict__[attribute] == expected.__dict__[attribute]
