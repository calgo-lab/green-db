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
                "start_urls": f"https://www.zalando.de/{path}/?cause={'.'.join(filters)}",
                "category": category,
                "meta_data": json.dumps({"family": "FASHION", "sex": sex, **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "herrenbekleidung-shirts": "SHIRT",
        "herrenbekleidung-hemden": "SHIRT",
        "herrenbekleidung-sweatshirts-hoodies": "SWEATER",
        "herrenbekleidung-pullover-strickjacken": "SWEATER",
        "herrenbekleidung-jacken": "JACKET",
        "herrenbekleidung-maentel": "JACKET",
        "herrenbekleidung-anzuege": "SUIT",
        "herrenbekleidung-jeans": "JEANS",
        "herrenbekleidung-hosen": "PANT",
        "herrenbekleidung-hosen-shorts": "PANT",
        "herrenbekleidung-trainingsanzuege-jogger": "TRACKSUIT",
        "herrenbekleidung-waesche": "UNDERWEAR",
        "herrenbekleidung-nachtwaesche": "NIGHTWEAR",
        "herrenbekleidung-bademode": "SWIMMWEAR",
        # Shoes and Bags
        "herrenschuhe": "SHOES",
        "taschen-accessoires-taschen-herren": "BAG",
        # Sport
        "sports-herren-shirts": ("SHIRT", {"type": "SPORT"}),
        "sports-herren-jacken": ("JACKET", {"type": "SPORT"}),
        "sporthosen-herren": ("PANT", {"type": "SPORT"}),
        "sports-herren-pullover-sweater": ("SWEATER", {"type": "SPORT"}),
        "trainingsanzug-herren": ("TRACKSUIT", {"type": "SPORT"}),
        "funktionsunterwaesche-herren": ("UNDERWEAR", {"type": "SPORT"}),
        "sports-herren-struempfe": ("UNDERWEAR", {"type": "SPORT"}),
        "sports-bademode-herren": ("SWIMMWEAR", {"type": "SPORT"}),
        "sportschuhe-herren": ("SHOES", {"type": "SPORT"}),
        "sports-taschen-rucksaecke-herren": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="MALE")


def female() -> List[dict]:
    path_2_category = {
        "damenbekleidung-kleider": "DRESS",
        "damenbekleidung-shirts": "SHIRT",
        "damenbekleidung-blusen-tuniken": "BLOUSE",
        "damenbekleidung-pullover-und-strickjacken": "SWEATER",
        "damenbekleidung-sweatshirts-hoodies": "SWEATER",
        "damenbekleidung-jacken": "JACKET",
        "damenbekleidung-maentel": "JACKET",
        "damenbekleidung-jeans": "JEANS",
        "damenbekleidung-hosen": "PANT",
        "damenbekleidung-hosen-shorts": "PANT",
        "damenbekleidung-hosen-overalls-jumpsuit": "OVERALL",
        "damenbekleidung-roecke": "SKIRT",
        "damenbekleidung-waesche": "UNDERWEAR",
        "nachtwaesche": "NIGHTWEAR",
        "damenbekleidung-struempfe": "UNDERWEAR",
        "damenbekleidung-bademode": "SWIMMWEAR",
        # Shoes and Bags
        "damenschuhe": "SHOES",
        "taschen-accessoires-taschen-damen": "BAG",
        # Sport
        "sports-damen-shirts": ("SHIRT", {"type": "SPORT"}),
        "sports-jacken-damen": ("JACKET", {"type": "SPORT"}),
        "sporthosen-damen": ("PANT", {"type": "SPORT"}),
        "sports-damen-pullover-sweater": ("SWEATER", {"type": "SPORT"}),
        "sports-kleider-roecke": ("DRESS", {"type": "SPORT"}),
        "sport-bh": ("UNDERWEAR", {"type": "SPORT"}),
        "funktionsunterwaesche-damen": ("UNDERWEAR", {"type": "SPORT"}),
        "sports-damen-struempfe": ("UNDERWEAR", {"type": "SPORT"}),
        "sportanzuege-damen": ("TRACKSUIT", {"type": "SPORT"}),
        "sports-bademode-damen": ("SWIMMWEAR", {"type": "SPORT"}),
        "sportschuhe-damen": ("SHOES", {"type": "SPORT"}),
        "sports-taschen-rucksaecke-damen": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="FEMALE")


def get_settings() -> List[dict]:
    return male() + female()
