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
        "/t-shirts-basiques-homme/": ProductCategory.TSHIRT.value,
        "/t-shirts-imprimes-homme/": ProductCategory.TSHIRT.value,
        "/debardeur-homme/": ProductCategory.SHIRT.value,
        "/polos-homme/": ProductCategory.SHIRT.value,
        "/t-shirts-manches-longues-homme/": ProductCategory.TSHIRT.value,
        "/t-shirt-sport-homme/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/chemises-homme/": ProductCategory.SHIRT.value,
        "/sweatshirts-hoodies-homme/": ProductCategory.SWEATER.value,
        "/pulls-gilets-homme/": ProductCategory.SWEATER.value,
        "/vestes-homme/": ProductCategory.JACKET.value,
        "/manteaux-homme/": ProductCategory.JACKET.value,
        "/costumes-homme/": ProductCategory.SUIT.value,
        "/jeans-homme/": ProductCategory.JEANS.value,
        "/pantalons-homme/": ProductCategory.PANTS.value,
        "/shorts-bermudas-homme/": ProductCategory.PANTS.value,
        "/joggings-survetements-homme/": ProductCategory.TRACKSUIT.value,
        "/slips-calecons-homme/": ProductCategory.UNDERWEAR.value,
        "/maillots-corps-homme/": ProductCategory.UNDERWEAR.value,
        "/chaussettes-homme/": ProductCategory.SOCKS.value,
        "/poignoirs-robes-de-chambre-homme/": ProductCategory.UNDERWEAR.value,
        "/pyjamas-homme/": ProductCategory.NIGHTWEAR.value,
        "/maillots-peignoirs-homme/": ProductCategory.SWIMWEAR.value,
        "/t-shirts-techniques-homme/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/tops-homme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sport-polos-homme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sport-t-shirts-manches-longues-homme/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sport-chemises-homme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/maillots-entrainement-homme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/vestes-polaires-homme/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/pantalons-sport-homme/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/pulls-sweatshirts-homme/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/survetements-homme/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/sport-sous-vetements-homme/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/sport-chaussettes-homme/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/vetements-plage-homme/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/chaussures-running-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/baskets-sport-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-randonnee-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-football-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-basketball-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-tennis-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-golf-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-fitness-sports-salle-sport-homme/": (
            ProductCategory.SNEAKERS.value,
            {"type": "SPORT"},
        ),
        "/chaussures-cyclisme-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-plage-homme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/bottes-boots-sport-homme/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/sacs-et-sacs-a-dos-sport-homme/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/baskets-homme/": ProductCategory.SNEAKERS.value,
        "/chaussures-basses-homme/": ProductCategory.SHOES.value,
        "/sandale-homme/": ProductCategory.SHOES.value,
        "/derbies-richelieus-homme/": ProductCategory.SHOES.value,
        "/chaussures-ville-homme/": ProductCategory.SHOES.value,
        "/boots-chaussure-montante-homme/": ProductCategory.SHOES.value,
        "/chaussons-homme/": ProductCategory.SHOES.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/robes-femme/": ProductCategory.DRESS.value,
        "/t-shirts-femme/": ProductCategory.TSHIRT.value,
        "/debardeurs-femme/": ProductCategory.SHIRT.value,
        "/polos-femme/": ProductCategory.SHIRT.value,
        "/t-shirts-manches-longues-femme/": ProductCategory.TSHIRT.value,
        "/chemisiers-tuniques-femme/": ProductCategory.BLOUSE.value,
        "/pulls-gilets-femme/": ProductCategory.SWEATER.value,
        "/sweatshirts-hoodies-femme/": ProductCategory.SWEATER.value,
        "/vestes-femme/": ProductCategory.JACKET.value,
        "/manteaux-femme/": ProductCategory.JACKET.value,
        "/jeans-femme/": ProductCategory.JEANS.value,
        "/pantalons-femme/": ProductCategory.PANTS.value,
        "/shorts-femme/": ProductCategory.PANTS.value,
        "/combinaisons-salopettes-femme/": ProductCategory.OVERALL.value,
        "/jupes-femme/": ProductCategory.SKIRT.value,
        "/lingerie-femme/": ProductCategory.UNDERWEAR.value,
        "/nuisettes-pyjamas-femme/": ProductCategory.NIGHTWEAR.value,
        "/collants-chaussettes-femme/": ProductCategory.SOCKS.value,
        "/maillots-peignoirs-femme/": ProductCategory.SWIMWEAR.value,
        "/t-shirts-techniques-femme/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sport-polos-femme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/tops-femme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sport-t-shirts-manches-longues-femme/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/chemisiers-femme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/maillots-entrainement-femme/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/vestes-polaires-femme/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/pantalons-sport-femme/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/pulls-sweatshirts-femme/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/robes-jupes-sport-femme/": (ProductCategory.DRESS.value, {"type": "SPORT"}),
        "/soutiens-gorge-sport-femme/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/sous-vetements-femme/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/chaussettes-femme/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/combinaisons-fitness-femme/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/vetements-plage-femme/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/chaussures-running-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-randonnee-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-tennis-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-golf-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-fitness-sports-salle-sport-femme/": (
            ProductCategory.SNEAKERS.value,
            {"type": "SPORT"},
        ),
        "/chaussures-sport-salle-training-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-plage-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-football-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/bottes-boots-sport-femme/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/chaussures-cyclisme-femme/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/sacs-a-dos-sport-femme/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/baskets-femme/": ProductCategory.SNEAKERS.value,
        "/chaussures-plates/": ProductCategory.SHOES.value,
        "/sandales-nu-pieds-femme/": ProductCategory.SHOES.value,
        "/sandales-de-bain-femme/": ProductCategory.SHOES.value,
        "/mules-sabots-femme/": ProductCategory.SHOES.value,
        "/ballerines-femme/": ProductCategory.SHOES.value,
        "/escarpins-femme/": ProductCategory.SHOES.value,
        "/talons-hauts-femme/": ProductCategory.SHOES.value,
        "/chaussures-mariee-femme/": ProductCategory.SHOES.value,
        "/bottines-femme/": ProductCategory.SHOES.value,
        "/bottes-femme/": ProductCategory.SHOES.value,
        "/chaussons-femme/": ProductCategory.SHOES.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
