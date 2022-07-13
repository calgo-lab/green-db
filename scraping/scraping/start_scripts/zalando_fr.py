import json
from typing import List

from core.domain import ConsumerLifestageType, GenderType, ProductCategory


def combine_results(
    path_2_category: dict,
    gender: str,
    consumer_lifestage: str,
    filters: list = [
        "animal_welfare",
        "fair_conditions",
        "reducing_emissions",
        "reusing_materials",
        "sustainable_beauty",
        "water_saving",
    ],
) -> List[dict]:
    results = []
    for path, info in path_2_category.items():
        category, meta_data = info if type(info) == tuple else (info, {})
        results.append(
            {
                "start_urls": f"https://www.zalando.fr/{path}/?cause={'.'.join(filters)}",
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps({"family": "FASHION", **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "/t-shirts-basiques-homme/": ProductCategory.TSHIRT,
        "/t-shirts-imprimes-homme/": ProductCategory.TSHIRT,
        "/debardeur-homme/": ProductCategory.SHIRT,
        "/polos-homme/": ProductCategory.SHIRT,
        "/t-shirts-manches-longues-homme/": ProductCategory.TSHIRT,
        "/t-shirt-sport-homme/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/chemises-homme/": ProductCategory.SHIRT,
        "/sweatshirts-hoodies-homme/": ProductCategory.SWEATER,
        "/pulls-gilets-homme/": ProductCategory.SWEATER,
        "/vestes-homme/": ProductCategory.JACKET,
        "/manteaux-homme/": ProductCategory.JACKET,
        "/costumes-homme/": ProductCategory.SUIT,
        "/jeans-homme/": ProductCategory.JEANS,
        "/pantalons-homme/": ProductCategory.PANTS,
        "/shorts-bermudas-homme/": ProductCategory.PANTS,
        "/joggings-survetements-homme/": ProductCategory.TRACKSUIT,
        "/slips-calecons-homme/": ProductCategory.UNDERWEAR,
        "/maillots-corps-homme/": ProductCategory.UNDERWEAR,
        "/chaussettes-homme/": ProductCategory.SOCKS,
        "/poignoirs-robes-de-chambre-homme/": ProductCategory.UNDERWEAR,
        "/pyjamas-homme/": ProductCategory.NIGHTWEAR,
        "/maillots-peignoirs-homme/": ProductCategory.SWIMWEAR,
        "/t-shirts-techniques-homme/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/tops-homme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sport-polos-homme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sport-t-shirts-manches-longues-homme/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sport-chemises-homme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/maillots-entrainement-homme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/vestes-polaires-homme/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/pantalons-sport-homme/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/pulls-sweatshirts-homme/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/survetements-homme/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/sport-sous-vetements-homme/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sport-chaussettes-homme/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/vetements-plage-homme/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/chaussures-running-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/baskets-sport-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-randonnee-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-football-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-basketball-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-tennis-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-golf-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-fitness-sports-salle-sport-homme/": (
            ProductCategory.SNEAKERS,
            {"type": "SPORT"},
        ),
        "/chaussures-cyclisme-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-plage-homme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/bottes-boots-sport-homme/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/sacs-et-sacs-a-dos-sport-homme/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/baskets-homme/": ProductCategory.SNEAKERS,
        "/chaussures-basses-homme/": ProductCategory.SHOES,
        "/sandale-homme/": ProductCategory.SHOES,
        "/derbies-richelieus-homme/": ProductCategory.SHOES,
        "/chaussures-ville-homme/": ProductCategory.SHOES,
        "/boots-chaussure-montante-homme/": ProductCategory.SHOES,
        "/chaussons-homme/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/robes-femme/": ProductCategory.DRESS,
        "/t-shirts-femme/": ProductCategory.TSHIRT,
        "/debardeurs-femme/": ProductCategory.SHIRT,
        "/polos-femme/": ProductCategory.SHIRT,
        "/t-shirts-manches-longues-femme/": ProductCategory.TSHIRT,
        "/chemisiers-tuniques-femme/": ProductCategory.BLOUSE,
        "/pulls-gilets-femme/": ProductCategory.SWEATER,
        "/sweatshirts-hoodies-femme/": ProductCategory.SWEATER,
        "/vestes-femme/": ProductCategory.JACKET,
        "/manteaux-femme/": ProductCategory.JACKET,
        "/jeans-femme/": ProductCategory.JEANS,
        "/pantalons-femme/": ProductCategory.PANTS,
        "/shorts-femme/": ProductCategory.PANTS,
        "/combinaisons-salopettes-femme/": ProductCategory.OVERALL,
        "/jupes-femme/": ProductCategory.SKIRT,
        "/lingerie-femme/": ProductCategory.UNDERWEAR,
        "/nuisettes-pyjamas-femme/": ProductCategory.NIGHTWEAR,
        "/collants-chaussettes-femme/": ProductCategory.SOCKS,
        "/maillots-peignoirs-femme/": ProductCategory.SWIMWEAR,
        "/t-shirts-techniques-femme/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sport-polos-femme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/tops-femme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sport-t-shirts-manches-longues-femme/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/chemisiers-femme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/maillots-entrainement-femme/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/vestes-polaires-femme/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/pantalons-sport-femme/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/pulls-sweatshirts-femme/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/robes-jupes-sport-femme/": (ProductCategory.DRESS, {"type": "SPORT"}),
        "/soutiens-gorge-sport-femme/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sous-vetements-femme/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/chaussettes-femme/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/combinaisons-fitness-femme/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/vetements-plage-femme/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/chaussures-running-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-randonnee-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-tennis-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-golf-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-fitness-sports-salle-sport-femme/": (
            ProductCategory.SNEAKERS,
            {"type": "SPORT"},
        ),
        "/chaussures-sport-salle-training-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-plage-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-football-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/bottes-boots-sport-femme/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/chaussures-cyclisme-femme/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/sacs-a-dos-sport-femme/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/baskets-femme/": ProductCategory.SNEAKERS,
        "/chaussures-plates/": ProductCategory.SHOES,
        "/sandales-nu-pieds-femme/": ProductCategory.SHOES,
        "/sandales-de-bain-femme/": ProductCategory.SHOES,
        "/mules-sabots-femme/": ProductCategory.SHOES,
        "/ballerines-femme/": ProductCategory.SHOES,
        "/escarpins-femme/": ProductCategory.SHOES,
        "/talons-hauts-femme/": ProductCategory.SHOES,
        "/chaussures-mariee-femme/": ProductCategory.SHOES,
        "/bottines-femme/": ProductCategory.SHOES,
        "/bottes-femme/": ProductCategory.SHOES,
        "/chaussons-femme/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
