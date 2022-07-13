import json
from typing import List

from core.domain import ConsumerLifestageType, GenderType, ProductCategory


def combine_results(
    path_2_category: dict,
    gender: str,
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
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps({"family": "FASHION", **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "/mens-clothing-basic-t-shirts/": ProductCategory.TSHIRT,
        "/mens-clothing-print-t-shirts/": ProductCategory.TSHIRT,
        "/mens-clothing-vests/": ProductCategory.SHIRT,
        "/mens-clothing-polo-shirts/": ProductCategory.SHIRT,
        "/mens-clothing-long-sleeve-tops/": ProductCategory.TSHIRT,
        "/mens-sports-t-shirts/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/mens-clothing-shirts/": ProductCategory.SHIRT,
        "/sweatshirts-hoodies-men/": ProductCategory.SWEATER,
        "/mens-clothing-jumpers-cardigans/": ProductCategory.SWEATER,
        "/mens-clothing-jackets/": ProductCategory.JACKET,
        "/mens-clothing-coats/": ProductCategory.JACKET,
        "/mens-clothing-suits-ties/": ProductCategory.SUIT,
        "/mens-clothing-jeans/": ProductCategory.JEANS,
        "/mens-clothing-trousers/": ProductCategory.PANTS,
        "/mens-clothing-shorts/": ProductCategory.PANTS,
        "/men-clothing-tracksuits/": ProductCategory.TRACKSUIT,
        "/mens-clothing-underpants/": ProductCategory.UNDERWEAR,
        "/mens-vests/": ProductCategory.UNDERWEAR,
        "/mens-clothing-socks/": ProductCategory.SOCKS,
        "/mens-underwear-dressing-gowns/": ProductCategory.UNDERWEAR,
        "/mens-clothing-nightwear/": ProductCategory.NIGHTWEAR,
        "/mens-clothing-swimwear/": ProductCategory.SWIMWEAR,
        "/mens-sports-plain-t-shirts/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/mens-sports-tank-tops/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/mens-sports-polo-shirts/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/mens-sports-long-sleeve-tops/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sports-shirts/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-jerseys-men/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/mens-sports-jackets-gilets/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/mens-sports-shorts-trousers/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/mens-sports-jumpers-sweatshirts/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/mens-tracksuits/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/mens-base-layers/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/mens-clothing-sports-socks/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/mens-sports-swimwear/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/mens-running-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/indoor-football-shoes-training-shoes-men/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-outdoor-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-football-boots/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-basketball-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-tennis-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-golf-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-trainers-fitness-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-cycling-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-beach-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/mens-sports-boots/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/sports-backpacks-bags-men/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/mens-shoes-trainers/": ProductCategory.SNEAKERS,
        "/mens-shoes-lace-up-shoes/": ProductCategory.SHOES,
        "/mens-shoes-flat-shoes/": ProductCategory.SHOES,
        "/mens-shoes-business-shoes/": ProductCategory.SHOES,
        "/mens-shoes-sandals/": ProductCategory.SHOES,
        "/mens-shoes-boots/": ProductCategory.SHOES,
        "/mens-shoes-slippers/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/womens-clothing-dresses/": ProductCategory.DRESS,
        "/womens-clothing-tops-t-shirts/": ProductCategory.TSHIRT,
        "/womens-clothing-tops-tops/": ProductCategory.SHIRT,
        "/womens-clothing-tops-polo-shirts/": ProductCategory.SHIRT,
        "/womens-clothing-tops-long-sleeve-tops/": ProductCategory.TSHIRT,
        "/womens-clothing-blouses-tunics/": ProductCategory.BLOUSE,
        "/womens-clothing-jumpers-cardigans/": ProductCategory.SWEATER,
        "/womens-clothing-pullovers-and-cardigans/": ProductCategory.SWEATER,
        "/womens-clothing-jackets/": ProductCategory.JACKET,
        "/womens-clothing-coats/": ProductCategory.JACKET,
        "/womens-clothing-jeans/": ProductCategory.JEANS,
        "/womens-clothing-trousers/": ProductCategory.PANTS,
        "/womens-clothing-shorts/": ProductCategory.PANTS,
        "/womens-clothing-playsuits-jumpsuits/": ProductCategory.OVERALL,
        "/womens-clothing-skirts/": ProductCategory.SKIRT,
        "/womens-clothing-underwear/": ProductCategory.UNDERWEAR,
        "/nightwear/": ProductCategory.NIGHTWEAR,
        "/womens-clothing-tights-socks/": ProductCategory.SOCKS,
        "/womens-clothing-swimwear/": ProductCategory.SWIMWEAR,
        "/womens-sports-plain-t-shirts/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/womens-sports-polo-shirts/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/womens-sports-tops/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/womens-sports-long-sleeve-tops/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/womens-sports-blouses/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-women-jerseys/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/womens-sports-jackets-gilets/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/womens-sports-shorts-trousers/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/womens-sports-jumpers-sweatshirts/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/womens-sports-dresses-skirts/": (ProductCategory.DRESS, {"type": "SPORT"}),
        "/womens-sports-bras/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/womens-base-layers/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/womens-sports-socks/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sportsuit-women/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/womens-sports-swimwear/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/womens-running-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-outdoor-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-tennis-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-golf-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-basketball-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-indoor-sports-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-beach-shoes/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-football-boots/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-sports-boots/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/womens-cycling-shoes/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/womens-bags-sports/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/womens-shoes-trainers/": ProductCategory.SNEAKERS,
        "/womens-shoes-ankle-boots/": ProductCategory.SHOES,
        "/womens-shoes-boots/": ProductCategory.SHOES,
        "/womens-shoes-sandals/": ProductCategory.SHOES,
        "/womens-shoes-heels/": ProductCategory.SHOES,
        "/womens-shoes-bridal-shoes/": ProductCategory.SHOES,
        "/womens-shoes-flats-lace-ups/": ProductCategory.SHOES,
        "/womens-shoes-ballet-pumps/": ProductCategory.SHOES,
        "/womens-shoes-mules-clogs/": ProductCategory.SHOES,
        "/womens-shoes-slippers/": ProductCategory.SHOES,
        "/flip-flops-beach-shoes/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
