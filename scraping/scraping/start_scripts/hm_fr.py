import json
from logging import getLogger
from typing import List

from core.domain import ConsumerLifestageType, GenderType
from scraping.utils import get_json_data

logger = getLogger(__name__)

categories = get_json_data("hm_fr_male_female.json")
gender_to_category = {GenderType.FEMALE.value: "femme", GenderType.MALE.value: "homme"}


def combine_results(
    gender: str,
    consumer_lifestage: str,
    serp_api: str = "https://www2.hm.com//fr_fr/",
    serp_filters: str = "/developpement-durable/our-products/_jcr_content/main/productlisting"
    ".display.json?sort=stock&image-size=small&image=model&offset=0&page-size"
    "=576",
) -> List[dict]:
    results = []
    for info in categories:
        mapping = info.get("category")
        if mapping:  # exclude categories for which we do not have a mapping yet
            product_filters = "&".join(f"{k}={v}" for k, v in info["filters"].items())
            category, meta_data = (mapping, {}) if isinstance(mapping, str) else mapping
            if gender in info["gender"]:
                results.append(
                    {
                        "start_urls": f"{serp_api}{gender_to_category[gender]}"
                        f"{serp_filters}&{product_filters}",
                        "category": category,
                        "gender": gender,
                        "consumer_lifestage": consumer_lifestage,
                        "meta_data": json.dumps({"family": "FASHION", **meta_data}),
                    }
                )
    return results


def male() -> List[dict]:
    return combine_results(
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    durable_categories = combine_results(
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )
    higg_categories = combine_results(
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        serp_filters="/developpement-durable/9333-higgindex-womens/_jcr_content/productlisting."
        "display.json?sort=stock&image-size=small&image=stillLife&offset=0&page-size"
        "=576",
    )
    return durable_categories + higg_categories


def get_settings() -> List[dict]:
    return male() + female()
