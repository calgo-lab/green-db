import json
from typing import Dict, List, Tuple, Union

gender_to_category = {
    "female": 28981,
    "male": 28982
}


def read_json(path):
    with open(path, "r", encoding="utf8") as f:
        return json.loads(f.read())


def combine_results(gender_mapping: dict,
                    gender: str,
                    categories_json_path: str = "../data/asos_product_types.json",
                    serp_api: str = "https://www.asos.com/api/product/search/v2/categories/",
                    serp_filters: str = "&channel=mobile-web&country=FR&currency=EUR"
                                   "&keyStoreDataversion=dup0qtf-35&lang=fr-FR&limit=72&offset=0"
                                   "&rowlength=2&store=FR "
                    ) -> List[dict]:
    results = []
    categories = read_json(categories_json_path)
    for id, info in categories.items():
        if gender in info.get("gender"):
            mapping = info.get("mapping")
            category, meta_data = mapping if type(mapping) == list else (mapping, {})
            results.append(
                {
                    "start_urls": f"{serp_api}{gender_mapping.get(gender)}"
                                  f"?attribute_1047={id}{serp_filters}",
                    "category": category,
                    "meta_data": json.dumps({"family": "FASHION", "sex": gender, **meta_data}),
                }
            )
    return results


def male():
    return combine_results(gender_mapping=gender_to_category, gender="male")


def female():
    return combine_results(gender_mapping=gender_to_category, gender="female")


def get_settings() -> List[Union[Dict[str, str], Dict[str, Tuple[str, Dict[str, str]]]]]:
    return male() + female()
