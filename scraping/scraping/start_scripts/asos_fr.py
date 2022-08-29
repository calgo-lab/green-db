import json
import pkgutil
from logging import getLogger
from typing import List

from core.domain import ConsumerLifestageType, GenderType
from scraping.utils import get_json_data

logger = getLogger(__name__)

categories = get_json_data("asos_product_types.json")
gender_to_category = {GenderType.FEMALE.value: 28981, GenderType.MALE.value: 28982}


def combine_results(
    gender: str,
    consumer_lifestage: str,
    serp_api: str = "https://www.asos.com/api/product/search/v2/categories/",
    serp_filters: str = "&channel=mobile-web&country=FR&currency=EUR"
    "&keyStoreDataversion=dup0qtf-35&lang=fr-FR&limit=72&offset=0"
    "&rowlength=2&store=FR",
) -> List[dict]:
    results = []
    for id, info in categories.items():
        mapping = info.get("category")
        if mapping:  # exclude categories for which we do not have a mapping yet
            if gender in info.get("gender"):
                category, meta_data = (mapping, {}) if isinstance(mapping, str) else mapping
                results.append(
                    {
                        "start_urls": f"{serp_api}{gender_to_category[gender]}"
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
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    return combine_results(
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
