import json
from typing import List


def combine_results(
    path_2_category: dict,
    sex: str,
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
                "meta_data": json.dumps({"family": "FASHION", "sex": sex, **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "t-shirts-polos-homme": "SHIRT",
        "chemises-homme": "SHIRT",
        "sweatshirts-hoodies-homme": "SWEATER",
        "pulls-gilets-homme": "SWEATER",
        "vestes-homme": "JACKET",
        "manteaux-homme": "JACKET",
        "costumes-homme": "SUIT",
        "jeans-homme": "JEANS",
        "pantalons-homme": "PANT",
        "shorts-bermudas-homme": "PANT",
        "joggings-survetements-homme": "TRACKSUIT",
        "sous-vetements-homme": "UNDERWEAR",
        "pyjamas-homme": "NIGHTWEAR",
        "maillots-peignoirs-homme": "SWIMWEAR",
        # Shoes and Bags
        "chaussures-homme": "SHOES",
        "sacs-accessoires-homme": "BAG",
        # Sport
        "t-shirts-tops-homme": ("SHIRT", {"type": "SPORT"}),
        "vestes-polaires-homme": ("JACKET", {"type": "SPORT"}),
        "pantalons-sport-homme": ("PANT", {"type": "SPORT"}),
        "pulls-sweatshirts-homme": ("SWEATER", {"type": "SPORT"}),
        "survetements-homme": ("TRACKSUIT", {"type": "SPORT"}),
        "sport-sous-vetements-homme": ("UNDERWEAR", {"type": "SPORT"}),
        "sport-chaussettes-homme": ("UNDERWEAR", {"type": "SPORT"}),
        "vetements-plage-homme": ("SWIMMWEAR", {"type": "SPORT"}),
        "sport-chaussures-homme": ("SHOES", {"type": "SPORT"}),
        "sacs-et-sacs-a-dos-sport-homme": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="MALE")


def female() -> List[dict]:
    path_2_category = {
        "robes-femme": "DRESS",
        "t-shirts-tops-femme": "SHIRT",
        "chemisiers-tuniques-femme": "BLOUSE",
        "pulls-gilets-femme": "SWEATER",
        "sweatshirts-hoodies-femme": "SWEATER",
        "vestes-femme": "JACKET",
        "manteaux-femme": "JACKET",
        "jeans-femme": "JEANS",
        "pantalons-femme": "PANT",
        "shorts-femme": "PANT",
        "combinaisons-salopettes-femme": "OVERALL",
        "jupes-femme": "SKIRT",
        "lingerie-femme": "UNDERWEAR",
        "nuisettes-pyjamas-femme": "NIGHTWEAR",
        "collants-chaussettes-femme": "UNDERWEAR",
        "maillots-peignoirs-femme": "SWIMMWEAR",
        # Shoes and Bags
        "chaussures-femme": "SHOES",
        "sacs-accessoires-femme": "BAG",
        # Sport
        "sport-t-shirts-tops-femme": ("SHIRT", {"type": "SPORT"}),
        "vestes-polaires-femme": ("JACKET", {"type": "SPORT"}),
        "pantalons-sport-femme": ("PANT", {"type": "SPORT"}),
        "pulls-sweatshirts-femme": ("SWEATER", {"type": "SPORT"}),
        "robes-jupes-sport-femme": ("DRESS", {"type": "SPORT"}),
        "soutiens-gorge-sport-femme": ("UNDERWEAR", {"type": "SPORT"}),
        "sous-vetements-femme": ("UNDERWEAR", {"type": "SPORT"}),
        "chaussettes-femme": ("UNDERWEAR", {"type": "SPORT"}),
        "combinaisons-fitness-femme": ("TRACKSUIT", {"type": "SPORT"}),
        "vetements-plage-femme": ("SWIMMWEAR", {"type": "SPORT"}),
        "sport-chaussures-femme": ("SHOES", {"type": "SPORT"}),
        "sacs-a-dos-sport-femme": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="FEMALE")


def get_settings() -> List[dict]:
    return male() + female()
