import json
import pkgutil
from logging import getLogger
from typing import List

logger = getLogger(__name__)

gender_to_category = {"FEMALE": "femme", "MALE": "homme"}

hm_file_path = "data/hm_fr_male_female.json"


def read_json(path: str) -> dict:
    if data := pkgutil.get_data("scraping", path):
        return json.loads(data.decode("utf-8"))
    else:
        logger.error(f"Unable to read {path}")
        return {}


def combine_results(
    gender_mapping: dict,
    gender: str,
    consumer_lifestage: str,
    categories_json_path: str,
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
                        "gender": gender,
                        "consumer_lifestage": consumer_lifestage,
                        "meta_data": json.dumps({"family": "FASHION", **meta_data}),
                    }
                )
    return results


def male() -> List[dict]:
    return combine_results(
        gender_mapping=gender_to_category,
        gender="MALE",
        consumer_lifestage="ADULT",
        categories_json_path=hm_file_path,
    )


def female() -> List[dict]:
    durable_categories = combine_results(
        gender_mapping=gender_to_category,
        gender="FEMALE",
        consumer_lifestage="ADULT",
        categories_json_path=hm_file_path,
    )
    higg_categories = combine_results(
        gender_mapping=gender_to_category,
        gender="FEMALE",
        consumer_lifestage="ADULT",
        categories_json_path=hm_file_path,
        serp_filters="/developpement-durable/9333-higgindex-womens/_jcr_content/productlisting."
        "display.json?sort=stock&image-size=small&image=stillLife&offset=0&page-size"
        "=576",
    )
    return durable_categories + higg_categories


def get_settings() -> List[dict]:
    return male() + female()
