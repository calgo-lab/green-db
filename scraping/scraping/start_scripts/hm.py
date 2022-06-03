import json
import pkgutil
from pathlib import Path
from typing import List

gender_to_category = {"female": "femme", "male": "homme"}

hm_file_path = "data/hm_fr_male_female.json"


def read_json(path: Path) -> dict:
    return json.loads(pkgutil.get_data("scraping", path))


def combine_results(
    gender_mapping: dict,
    gender: str,
    categories_json_path: Path,
    serp_api: str = "https://www2.hm.com//fr_fr/",
    serp_filters: str = "/developpement-durable/our-products/_jcr_content/main/productlisting"
                        ".display.json?sort=stock&image-size=small&image=model&offset=0&page-size"
                        "=576",
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
                        f"{serp_filters}&productTypes={info.get('code')}",
                        "category": category,
                        "meta_data": json.dumps({"family": "FASHION", "sex": gender, **meta_data}),
                    }
                )
    return results


def male() -> List[dict]:
    return combine_results(
        gender_mapping=gender_to_category, gender="male", categories_json_path=hm_file_path
    )


def female() -> List[dict]:
    durable_categories = combine_results(
        gender_mapping=gender_to_category, gender="female", categories_json_path=hm_file_path
    )
    higg_categories = combine_results(
        gender_mapping=gender_to_category, gender="female", categories_json_path=hm_file_path,
        serp_filters = "/developpement-durable/9333-higgindex-womens/_jcr_content/productlisting."
                       "display.json?sort=stock&image-size=small&image=stillLife&offset=0&page-size"
                       "=576"
    )
    return durable_categories + higg_categories


def get_settings() -> List[dict]:
    return male() + female()
