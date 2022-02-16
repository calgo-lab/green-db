import json
from typing import Dict, List, Tuple, Union


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
        for filter in filters:
            results.append(
                {
                    "start_urls": f"https://www.zalando.de/{path}/?cause={filter}",
                    "category": category,
                    "meta_data": json.dumps(
                        {"family": "FASHION", "sustainability": filter, "sex": sex, **meta_data}
                    ),
                }
            )
    return results


def male() -> List[dict]:
    path_2_category = {
        "herrenbekleidung-shirts": "SHIRT",
        "sports-herren-shirts": ("SHIRT", {"type": "SPORT"}),
        "herrenbekleidung-hemden": "SHIRT",
        "herrenbekleidung-sweatshirts-hoodies": "SWEATER",
        "sports-herren-pullover-sweater": ("SWEATER", {"type": "SPORT"}),
        "herrenbekleidung-pullover-strickjacken": "SWEATER",
        "herrenbekleidung-jacken": "JACKET",
        "sports-herren-jacken": ("JACKET", {"type": "SPORT"}),
        "herrenbekleidung-maentel": "JACKET",
        "herrenbekleidung-anzuege": "SUIT",
        "herrenbekleidung-jeans": "JEANS",
        "herrenbekleidung-hosen": "PANT",
        "sporthosen-herren": ("PANT", {"type": "SPORT"}),
        "herrenbekleidung-hosen-shorts": ("PANT", {"type": "SHORTS"}),
        "herrenbekleidung-trainingsanzuege-jogger": "TRACKSUIT",
        "trainingsanzug-herren": ("TRACKSUIT", {"type": "SPORT"}),
        "herrenbekleidung-waesche": "UNDERWEAR",
        "herrenbekleidung-nachtwaesche": "NIGHTWEAR",
        "herrenbekleidung-bademode": "SWIMMWEAR",
        "funktionsunterwaesche-herren": ("UNDERWEAR", {"type": "SPORT"}),
        "sports-herren-struempfe": ("UNDERWEAR", {"type": "SPORT"}),
        "sports-bademode-herren": ("SWIMMWEAR", {"type": "SPORT"}),
        "sportschuhe-herren": ("SHOES", {"type": "SPORT"}),
        "herrenschuhe": "SHOES",
        "sports-taschen-rucksaecke-herren": ("BACKPACK", {"type": "SPORT"}),
        "taschen-accessoires-taschen-herren": "BAG",
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
        "damenbekleidung-jeans": "JEANS",
        "damenbekleidung-hosen": "PANT",
        "damenbekleidung-hosen-shorts": ("PANT", {"type": "SHORTS"}),
        "damenbekleidung-hosen-overalls-jumpsuit": "OVERALL",
        "damenbekleidung-roecke": "SKIRT",
        "damenbekleidung-waesche": "UNDERWEAR",
        "nachtwaesche": "NIGHTWEAR",
        "damenbekleidung-struempfe": "UNDERWEAR",
        "damenbekleidung-bademode": "SWIMMWEAR",
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
        "damenschuhe": "SHOES",
        "sports-taschen-rucksaecke-damen": ("BACKPACK", {"type": "SPORT"}),
        "taschen-accessoires-taschen-damen": "BAG",
    }

    return combine_results(path_2_category, sex="FEMALE")


def get_settings() -> List[Union[Dict[str, str], Dict[str, Tuple[str, Dict[str, str]]]]]:
    return male() + female()
