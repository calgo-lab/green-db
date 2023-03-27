import json
from logging import getLogger
from typing import List
from core.domain import ProductCategory


logger = getLogger(__name__)

path_2_category = {
        "smartphone": ProductCategory.SMARTPHONE.value,
        "pc-portable": ProductCategory.LAPTOP.value,
        "tablette-tactile": ProductCategory.TABLET.value,
        "tv": ProductCategory.TV.value,
        "imprimante": ProductCategory.PRINTER.value,

        "refrigerateur": ProductCategory.FRIDGE.value,
        "congelateur": ProductCategory.FREEZER.value,
        "lave-linge": ProductCategory.WASHER.value,
        "lave-vaisselle": ProductCategory.DISHWASHER.value,
        "seche-linge": ProductCategory.DRYER.value,
        "cuisiniere": ProductCategory.STOVE.value,
        "four": ProductCategory.OVEN.value,
}

def electronics(
    serp_api: str = 'https://www.e.leclerc/api/rest/live-api/product-search?language=fr-FR&size=30&sorts=%5B%5D&page=1&categories=%7B%22code%22:%5B%22NAVIGATION_{category}%22%5D%7D'
) -> List[dict]:
    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": serp_api.format(category=path),
                "category": category,
                "meta_data": json.dumps({"family": "electronics"}),
            }
        )
    return results


def get_settings() -> List[dict]:
    return electronics()
