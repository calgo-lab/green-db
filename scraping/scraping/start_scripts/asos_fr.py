import json
import pkgutil
from logging import getLogger
from typing import List

from core.domain import ConsumerLifestageType, GenderType

logger = getLogger(__name__)

gender_to_category = {GenderType.FEMALE.value: 28981, GenderType.MALE.value: 28982}

asos_file_path = "data/asos_product_types.json"


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
    serp_api: str = "https://www.asos.com/api/product/search/v2/categories/",
    serp_filters: str = "&channel=mobile-web&country=FR&currency=EUR"
    "&keyStoreDataversion=dup0qtf-35&lang=fr-FR&limit=72&offset=0"
    "&rowlength=2&store=FR",
) -> List[dict]:
    results = []
    categories = read_json(categories_json_path)
    for id, info in categories.items():
        mapping = info.get("category")
        if mapping:  # exclude categories for which we do not have a mapping yet
            if gender in info.get("gender"):
                category, meta_data = mapping if type(mapping) == list else (mapping, {})
                results.append(
                    {
                        "start_urls": f"{serp_api}{gender_mapping.get(gender)}"
                        f"?attribute_1047={id}{serp_filters}",
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
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        categories_json_path=asos_file_path,
    )


def female() -> List[dict]:
    return combine_results(
        gender_mapping=gender_to_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        categories_json_path=asos_file_path,
    )


def get_settings() -> List[dict]:
    return male() + female()
