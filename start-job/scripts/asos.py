import json
from pathlib import Path
from typing import List

gender_to_category = {"female": 28981, "male": 28982}

asos_file_path = Path(__file__).parent.parent / "data/asos_product_types.json"


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf8") as f:
        return json.loads(f.read())


def combine_results(
    gender_mapping: dict,
    gender: str,
    categories_json_path: Path,
    serp_api: str = "https://www.asos.com/api/product/search/v2/categories/",
    serp_filters: str = "&channel=mobile-web&country=FR&currency=EUR"
    "&keyStoreDataversion=dup0qtf-35&lang=fr-FR&limit=72&offset=0"
    "&rowlength=2&store=FR",
) -> List[dict]:
    results = []
    categories = read_json(categories_json_path)
    for id, info in categories.items():
        mapping = info.get("mapping")
        if mapping:  # exclude categories for which we do not have a mapping yet
            if gender in info.get("gender"):
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


def male() -> List[dict]:
    return combine_results(
        gender_mapping=gender_to_category, gender="male", categories_json_path=asos_file_path
    )


def female() -> List[dict]:
    return combine_results(
        gender_mapping=gender_to_category, gender="female", categories_json_path=asos_file_path
    )


def get_settings() -> List[dict]:
    return male() + female()
