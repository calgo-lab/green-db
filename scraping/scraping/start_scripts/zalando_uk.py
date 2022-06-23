import json
from typing import List


def combine_results(
    path_2_category: dict,
    sex: str,
    consumer_lifestage: str,
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
        results.append(
            {
                "start_urls": f"https://www.zalando.co.uk/{path}/?cause={'.'.join(filters)}",
                "category": category,
                "gender": sex,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps({"family": "FASHION", **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "mens-clothing-t-shirts": "SHIRT",
        "mens-clothing-shirts": "SHIRT",
        "sweatshirts-hoodies-men": "SWEATER",
        "mens-clothing-jumpers-cardigans": "SWEATER",
        "mens-clothing-jackets": "JACKET",
        "mens-clothing-coats": "JACKET",
        "mens-clothing-suits-ties": "SUIT",
        "mens-clothing-jeans": "JEANS",
        "mens-clothing-trousers": "PANT",
        "mens-clothing-shorts": "PANT",
        "men-clothing-tracksuits": "TRACKSUIT",
        "mens-clothing-underwear": "UNDERWEAR",
        "mens-clothing-nightwear": "NIGHTWEAR",
        "mens-clothing-swimwear": "SWIMMWEAR",
        # Shoes and Bags
        "mens-shoes": "SHOES",
        "bags-accessories-mens": "BAG",
        # Sport
        "mens-sports-shirts-tops": ("SHIRT", {"type": "SPORT"}),
        "mens-sports-jackets-gilets": ("JACKET", {"type": "SPORT"}),
        "mens-sports-shorts-trousers": ("PANT", {"type": "SPORT"}),
        "mens-sports-jumpers-sweatshirts": ("SWEATER", {"type": "SPORT"}),
        "mens-tracksuits": ("TRACKSUIT", {"type": "SPORT"}),
        "mens-base-layers": ("UNDERWEAR", {"type": "SPORT"}),
        "mens-clothing-sports-socks": ("UNDERWEAR", {"type": "SPORT"}),
        "mens-sports-swimwear": ("SWIMMWEAR", {"type": "SPORT"}),
        "mens-sports-shoes": ("SHOES", {"type": "SPORT"}),
        "sports-backpacks-bags-men": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="MALE", consumer_lifestage="ADULT")


def female() -> List[dict]:
    path_2_category = {
        "womens-clothing-dresses": "DRESS",
        "womens-clothing-tops": "SHIRT",
        "womens-clothing-blouses-tunics": "BLOUSE",
        "womens-clothing-jumpers-cardigans": "SWEATER",
        "womens-clothing-pullovers-and-cardigans": "SWEATER",
        "womens-clothing-jackets": "JACKET",
        "womens-clothing-coats": "JACKET",
        "womens-clothing-jeans": "JEANS",
        "womens-clothing-trousers": "PANT",
        "womens-clothing-shorts": "PANT",
        "womens-clothing-playsuits-jumpsuits": "OVERALL",
        "womens-clothing-skirts": "SKIRT",
        "womens-clothing-underwear": "UNDERWEAR",
        "nightwear": "NIGHTWEAR",
        "womens-clothing-tights-socks": "UNDERWEAR",
        "womens-clothing-swimwear": "SWIMMWEAR",
        # Shoes and Bags
        "womens-shoes": "SHOES",
        "bags-accessories-womens": "BAG",
        # Sport
        "womens-sports-shirts-tops": ("SHIRT", {"type": "SPORT"}),
        "womens-sports-jackets-gilets": ("JACKET", {"type": "SPORT"}),
        "womens-sports-shorts-trousers": ("PANT", {"type": "SPORT"}),
        "womens-sports-jumpers-sweatshirts": ("SWEATER", {"type": "SPORT"}),
        "womens-sports-dresses-skirts": ("DRESS", {"type": "SPORT"}),
        "womens-sports-bras": ("UNDERWEAR", {"type": "SPORT"}),
        "womens-base-layers": ("UNDERWEAR", {"type": "SPORT"}),
        "womens-sports-socks": ("UNDERWEAR", {"type": "SPORT"}),
        "sportsuit-women": ("TRACKSUIT", {"type": "SPORT"}),
        "womens-sports-swimwear": ("SWIMMWEAR", {"type": "SPORT"}),
        "womens-sports-shoes": ("SHOES", {"type": "SPORT"}),
        "womens-bags-sports": ("BAG", {"type": "SPORT"}),
    }

    return combine_results(path_2_category, sex="FEMALE", consumer_lifestage="ADULT")


def get_settings() -> List[dict]:
    return male() + female()
