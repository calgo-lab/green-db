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
                "start_urls": f"https://www.zalando.de/{path}/?cause={'.'.join(filters)}",
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps({"family": "FASHION", **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "/herrenbekleidung-shirts-basic/": ProductCategory.TSHIRT,
        "/herrenbekleidung-shirts-print/": ProductCategory.TSHIRT,
        "/herrenbekleidung-shirts-tops/": ProductCategory.SHIRT,
        "/herrenbekleidung-shirts-poloshirts/": ProductCategory.SHIRT,
        "/herrenbekleidung-shirts-longsleeves/": ProductCategory.TSHIRT,
        "/herrenbekleidung-shirts-sport/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/herrenbekleidung-hemden/": ProductCategory.SHIRT,
        "/herrenbekleidung-sweatshirts-hoodies/": ProductCategory.SWEATER,
        "/herrenbekleidung-pullover-strickjacken/": ProductCategory.SWEATER,
        "/herrenbekleidung-jacken/": ProductCategory.JACKET,
        "/herrenbekleidung-maentel/": ProductCategory.JACKET,
        "/herrenbekleidung-anzuege/": ProductCategory.SUIT,
        "/herrenbekleidung-jeans/": ProductCategory.JEANS,
        "/herrenbekleidung-hosen/": ProductCategory.PANTS,
        "/herrenbekleidung-hosen-shorts/": ProductCategory.PANTS,
        "/herrenbekleidung-trainingsanzuege-jogger/": ProductCategory.TRACKSUIT,
        "/unterhosen/": ProductCategory.UNDERWEAR,
        "/unterhemd-herren/": ProductCategory.UNDERWEAR,
        "/herrenbekleidung-struempfe-socken/": ProductCategory.SOCKS,
        "/herrenbekleidung-bademaentel/": ProductCategory.UNDERWEAR,
        "/herrenbekleidung-nachtwaesche/": ProductCategory.NIGHTWEAR,
        "/herrenbekleidung-bademode/": ProductCategory.SWIMWEAR,
        "/sports-herren-shirts-funktion/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sports-tanktops-herren/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-poloshirts-herren/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-langarmshirts-herren/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sports-herren-hemden/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-herren-shirts-trikot/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-herren-jacken/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/sporthosen-herren/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/sports-herren-pullover-sweater/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/trainingsanzug-herren/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/funktionsunterwaesche-herren/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sports-herren-struempfe/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sports-bademode-herren/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/laufschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/hallenschuhe-trainingsschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/sports-outdoorschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/fussballschuhe/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/basketballschuhe/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/tennisschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/golfschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/hallenschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/fahrradschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/badeschuhe-herren/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/stiefel-boots-herren/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/sports-taschen-rucksaecke-herren/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/herrenschuhe-sneaker/": ProductCategory.SNEAKERS,
        "/herrenschuhe-schnuerer/": ProductCategory.SHOES,
        "/herrenschuhe-halbschuhe/": ProductCategory.SHOES,
        "/herrenschuhe-business-schuhe/": ProductCategory.SHOES,
        "/herrenschuhe-offene-schuhe/": ProductCategory.SHOES,
        "/herrenschuhe-boots/": ProductCategory.SHOES,
        "/herrenschuhe-hausschuhe/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/damenbekleidung-kleider/": ProductCategory.DRESS,
        "/t-shirts-kurzarm/": ProductCategory.TSHIRT,
        "/damenbekleidung-tops/": ProductCategory.SHIRT,
        "/damenbekleidung-shirts-poloshirts/": ProductCategory.SHIRT,
        "/langarmshirt/": ProductCategory.TSHIRT,
        "/damenbekleidung-blusen-tuniken/": ProductCategory.BLOUSE,
        "/damenbekleidung-pullover-und-strickjacken/": ProductCategory.SWEATER,
        "/damenbekleidung-sweatshirts-hoodies/": ProductCategory.SWEATER,
        "/damenbekleidung-jacken/": ProductCategory.JACKET,
        "/damenbekleidung-jacken-maentel/": ProductCategory.JACKET,
        "/damenbekleidung-jeans/": ProductCategory.JEANS,
        "/damenbekleidung-hosen/": ProductCategory.PANTS,
        "/damenbekleidung-hosen-shorts/": ProductCategory.PANTS,
        "/damenbekleidung-hosen-overalls-jumpsuit/": ProductCategory.OVERALL,
        "/damenbekleidung-roecke/": ProductCategory.SKIRT,
        "/damenbekleidung-waesche/": ProductCategory.UNDERWEAR,
        "/nachtwaesche/": ProductCategory.NIGHTWEAR,
        "/damenbekleidung-struempfe/": ProductCategory.SOCKS,
        "/damenbekleidung-bademode/": ProductCategory.SWIMWEAR,
        "/sports-damen-shirts-funktion/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sports-poloshirts-damen/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-top-damen/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-langarmshirts-damen/": (ProductCategory.TSHIRT, {"type": "SPORT"}),
        "/sports-blusen-damen/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-damen-shirts-trikot/": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/sports-jacken-damen/": (ProductCategory.JACKET, {"type": "SPORT"}),
        "/sporthosen-damen/": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/sports-damen-pullover-sweater/": (ProductCategory.SWEATER, {"type": "SPORT"}),
        "/sports-kleider-roecke/": (ProductCategory.DRESS, {"type": "SPORT"}),
        "/sport-bh/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/funktionsunterwaesche-damen/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sports-damen-struempfe/": (ProductCategory.UNDERWEAR, {"type": "SPORT"}),
        "/sportanzuege-damen/": (ProductCategory.TRACKSUIT, {"type": "SPORT"}),
        "/sports-bademode-damen/": (ProductCategory.SWIMWEAR, {"type": "SPORT"}),
        "/laufschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/sports-outdoorschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/tennisschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/golfschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/hallenschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/hallenschuhe-trainingsschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/badeschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/damen-fussballschuhe/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/stiefel-boots-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/skischuhe-damen/": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/fahrradschuhe-damen/": (ProductCategory.SNEAKERS, {"type": "SPORT"}),
        "/sports-taschen-rucksaecke-damen/": (ProductCategory.BAG, {"type": "SPORT"}),
        "/damenschuhe-sneaker/": ProductCategory.SNEAKERS,
        "/damenschuhe-stiefeletten/": ProductCategory.SHOES,
        "/damenschuhe-stiefel/": ProductCategory.SHOES,
        "/damenschuhe-sandaletten/": ProductCategory.SHOES,
        "/damenschuhe-high-heels/": ProductCategory.SHOES,
        "/damenschuhe-pumps/": ProductCategory.SHOES,
        "/damenschuhe-brautschuhe/": ProductCategory.SHOES,
        "/flache-schuhe/": ProductCategory.SHOES,
        "/damenschuhe-ballerinas/": ProductCategory.SHOES,
        "/damenschuhe-pantoletten/": ProductCategory.SHOES,
        "/damenschuhe-hausschuhe/": ProductCategory.SHOES,
        "/damenschuhe-badeschuhe/": ProductCategory.SHOES,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
