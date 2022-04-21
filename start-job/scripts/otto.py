import json
from typing import List


def female_clothes() -> List[dict]:
    base_path = "https://www.otto.de/damen/mode"
    filter = "?nachhaltigkeit=alle-nachhaltigen-artikel"

    path_2_category = {
        "blazer": "SUIT",
        "blusen": "BLOUSE",
        "hosen": "PANT",
        "jacken": "JACKET",
        "kleider": "DRESS",
        "maentel": "JACKET",
        "overalls": "OVERALL",
        "pullover": "SWEATER",
        "roecke": "SKIRT",
        "shirts": "SHIRT",
        "tops": "TOP",
        "westen": "SWEATER",
        "bademode": "SWIMMWEAR",
        "waesche": "UNDERWEAR",
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"sex": "FEMALE", "family": "FASHION"}),
            }
        )
    return results


def male_clothes() -> List[dict]:
    base_path = "https://www.otto.de/herren/mode"
    filter = "?nachhaltigkeit=alle-nachhaltigen-artikel"

    path_2_category = {
        "bademode": "SWIMMWEAR",
        "waesche": "UNDERWEAR",
        "hemden": "SHIRT",
        "hosen": "PANT",
        "jacken": "JACKET",
        "maentel": "JACKET",
        "pullover": "SWEATER",
        "shirts": "SHIRT",
        "westen": "SWEATER",
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"sex": "MALE", "family": "FASHION"}),
            }
        )
    return results


def shoes() -> List[dict]:
    base_path = "https://www.otto.de"
    filter = "?nachhaltigkeit=alle-nachhaltigen-artikel"

    sex_to_path = {"MALE": "herren", "FEMALE": "damen"}

    results = []
    for sex, path in sex_to_path.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/schuhe/{filter}",
                "category": "SHOES",
                "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
            }
        )
    return results


def bags() -> List[dict]:
    base_path = "https://www.otto.de"
    filter = "?nachhaltigkeit=alle-nachhaltigen-artikel"

    sex_to_path = {"MALE": "herren", "FEMALE": "damen"}

    results = []
    for sex, path in sex_to_path.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/taschen/rucksaecke/{filter}",
                "category": "BACKPACK",
                "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
            }
        )
        results.append(
            {
                "start_urls": f"{base_path}/{path}/taschen/{filter}",
                "category": "BAG",
                "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
            }
        )
    return results


def household() -> List[dict]:
    base_path = "https://www.otto.de/haushalt"
    filter = "?nachhaltigkeit=alle-nachhaltigen-artikel"

    path_2_category = {
        "backoefen": "OVEN",
        "dunstabzugshauben": "COOKER_HOOD",
        "gefrierschraenke": "FREEZER",
        "geschirrspueler": "DISHWASHER",
        "herde": "STOVE",
        "kuehlschraenke": "FRIDGE",
        "trockner": "DRYER",
        "waschmaschinen": "WASHER",
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"family": "electronics"}),
            }
        )
    return results


def get_settings() -> List[dict]:
    return household() + bags() + shoes() + male_clothes() + female_clothes()
