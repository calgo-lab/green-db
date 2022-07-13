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
        "/mens-clothing-basic-t-shirts/": ProductCategory.TSHIRT.value,
        "/mens-clothing-print-t-shirts/": ProductCategory.TSHIRT.value,
        "/mens-clothing-vests/": ProductCategory.SHIRT.value,
        "/mens-clothing-polo-shirts/": ProductCategory.SHIRT.value,
        "/mens-clothing-long-sleeve-tops/": ProductCategory.TSHIRT.value,
        "/mens-sports-t-shirts/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/mens-clothing-shirts/": ProductCategory.SHIRT.value,
        "/sweatshirts-hoodies-men/": ProductCategory.SWEATER.value,
        "/mens-clothing-jumpers-cardigans/": ProductCategory.SWEATER.value,
        "/mens-clothing-jackets/": ProductCategory.JACKET.value,
        "/mens-clothing-coats/": ProductCategory.JACKET.value,
        "/mens-clothing-suits-ties/": ProductCategory.SUIT.value,
        "/mens-clothing-jeans/": ProductCategory.JEANS.value,
        "/mens-clothing-trousers/": ProductCategory.PANTS.value,
        "/mens-clothing-shorts/": ProductCategory.PANTS.value,
        "/men-clothing-tracksuits/": ProductCategory.TRACKSUIT.value,
        "/mens-clothing-underpants/": ProductCategory.UNDERWEAR.value,
        "/mens-vests/": ProductCategory.UNDERWEAR.value,
        "/mens-clothing-socks/": ProductCategory.SOCKS.value,
        "/mens-underwear-dressing-gowns/": ProductCategory.UNDERWEAR.value,
        "/mens-clothing-nightwear/": ProductCategory.NIGHTWEAR.value,
        "/mens-clothing-swimwear/": ProductCategory.SWIMWEAR.value,
        "/mens-sports-plain-t-shirts/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/mens-sports-tank-tops/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/mens-sports-polo-shirts/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/mens-sports-long-sleeve-tops/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sports-shirts/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-jerseys-men/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/mens-sports-jackets-gilets/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/mens-sports-shorts-trousers/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/mens-sports-jumpers-sweatshirts/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/mens-tracksuits/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/mens-base-layers/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/mens-clothing-sports-socks/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/mens-sports-swimwear/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/mens-running-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/indoor-football-shoes-training-shoes-men/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-outdoor-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-football-boots/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-basketball-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-tennis-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-golf-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-trainers-fitness-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-cycling-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-beach-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/mens-sports-boots/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/sports-backpacks-bags-men/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/mens-shoes-trainers/": ProductCategory.SNEAKERS.value,
        "/mens-shoes-lace-up-shoes/": ProductCategory.SHOES.value,
        "/mens-shoes-flat-shoes/": ProductCategory.SHOES.value,
        "/mens-shoes-business-shoes/": ProductCategory.SHOES.value,
        "/mens-shoes-sandals/": ProductCategory.SHOES.value,
        "/mens-shoes-boots/": ProductCategory.SHOES.value,
        "/mens-shoes-slippers/": ProductCategory.SHOES.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/womens-clothing-dresses/": ProductCategory.DRESS.value,
        "/womens-clothing-tops-t-shirts/": ProductCategory.TSHIRT.value,
        "/womens-clothing-tops-tops/": ProductCategory.SHIRT.value,
        "/womens-clothing-tops-polo-shirts/": ProductCategory.SHIRT.value,
        "/womens-clothing-tops-long-sleeve-tops/": ProductCategory.TSHIRT.value,
        "/womens-clothing-blouses-tunics/": ProductCategory.BLOUSE.value,
        "/womens-clothing-jumpers-cardigans/": ProductCategory.SWEATER.value,
        "/womens-clothing-pullovers-and-cardigans/": ProductCategory.SWEATER.value,
        "/womens-clothing-jackets/": ProductCategory.JACKET.value,
        "/womens-clothing-coats/": ProductCategory.JACKET.value,
        "/womens-clothing-jeans/": ProductCategory.JEANS.value,
        "/womens-clothing-trousers/": ProductCategory.PANTS.value,
        "/womens-clothing-shorts/": ProductCategory.PANTS.value,
        "/womens-clothing-playsuits-jumpsuits/": ProductCategory.OVERALL.value,
        "/womens-clothing-skirts/": ProductCategory.SKIRT.value,
        "/womens-clothing-underwear/": ProductCategory.UNDERWEAR.value,
        "/nightwear/": ProductCategory.NIGHTWEAR.value,
        "/womens-clothing-tights-socks/": ProductCategory.SOCKS.value,
        "/womens-clothing-swimwear/": ProductCategory.SWIMWEAR.value,
        "/womens-sports-plain-t-shirts/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/womens-sports-polo-shirts/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/womens-sports-tops/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/womens-sports-long-sleeve-tops/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/womens-sports-blouses/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-women-jerseys/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/womens-sports-jackets-gilets/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/womens-sports-shorts-trousers/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/womens-sports-jumpers-sweatshirts/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/womens-sports-dresses-skirts/": (ProductCategory.DRESS.value, {"type": "SPORT"}),
        "/womens-sports-bras/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/womens-base-layers/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/womens-sports-socks/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/sportsuit-women/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/womens-sports-swimwear/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/womens-running-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-outdoor-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-tennis-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-golf-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-basketball-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-indoor-sports-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-beach-shoes/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-football-boots/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-sports-boots/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "/womens-cycling-shoes/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/womens-bags-sports/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/womens-shoes-trainers/": ProductCategory.SNEAKERS.value,
        "/womens-shoes-ankle-boots/": ProductCategory.SHOES.value,
        "/womens-shoes-boots/": ProductCategory.SHOES.value,
        "/womens-shoes-sandals/": ProductCategory.SHOES.value,
        "/womens-shoes-heels/": ProductCategory.SHOES.value,
        "/womens-shoes-bridal-shoes/": ProductCategory.SHOES.value,
        "/womens-shoes-flats-lace-ups/": ProductCategory.SHOES.value,
        "/womens-shoes-ballet-pumps/": ProductCategory.SHOES.value,
        "/womens-shoes-mules-clogs/": ProductCategory.SHOES.value,
        "/womens-shoes-slippers/": ProductCategory.SHOES.value,
        "/flip-flops-beach-shoes/": ProductCategory.SHOES.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
