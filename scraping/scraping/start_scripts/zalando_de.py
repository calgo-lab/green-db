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
        "/herrenbekleidung-shirts-basic/": ProductCategory.TSHIRT.value,
        "/herrenbekleidung-shirts-print/": ProductCategory.TSHIRT.value,
        "/herrenbekleidung-shirts-tops/": ProductCategory.SHIRT.value,
        "/herrenbekleidung-shirts-poloshirts/": ProductCategory.SHIRT.value,
        "/herrenbekleidung-shirts-longsleeves/": ProductCategory.TSHIRT.value,
        "/herrenbekleidung-shirts-sport/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/herrenbekleidung-hemden/": ProductCategory.SHIRT.value,
        "/herrenbekleidung-sweatshirts-hoodies/": ProductCategory.SWEATER.value,
        "/herrenbekleidung-strickpullover/": ProductCategory.SWEATER.value,
        "/herrenbekleidung-strickjacken/": ProductCategory.JACKET.value,
        "/herrenbekleidung-jacken/": ProductCategory.JACKET.value,
        "/herrenbekleidung-maentel/": ProductCategory.JACKET.value,
        "/herrenbekleidung-anzuege/": ProductCategory.SUIT.value,
        "/herrenbekleidung-jeans/": ProductCategory.JEANS.value,
        "/herrenbekleidung-hosen/": ProductCategory.PANTS.value,
        "/herrenbekleidung-hosen-shorts/": ProductCategory.PANTS.value,
        "/herrenbekleidung-trainingsanzuege-jogger/": ProductCategory.TRACKSUIT.value,
        "/unterhosen/": ProductCategory.UNDERWEAR.value,
        "/unterhemd-herren/": ProductCategory.UNDERWEAR.value,
        "/herrenbekleidung-struempfe-socken/": ProductCategory.SOCKS.value,
        "/herrenbekleidung-bademaentel/": ProductCategory.NIGHTWEAR.value,
        "/herrenbekleidung-nachtwaesche/": ProductCategory.NIGHTWEAR.value,
        "/herrenbekleidung-bademode/": ProductCategory.SWIMWEAR.value,
        "/sports-herren-shirts-funktion/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sports-tanktops-herren/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-poloshirts-herren/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-langarmshirts-herren/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sports-herren-hemden/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-herren-shirts-trikot/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-herren-jacken/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/sporthosen-herren/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/sports-herren-pullover-sweater/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/trainingsanzug-herren/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/funktionsunterwaesche-herren/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/sports-herren-struempfe/": (ProductCategory.SOCKS.value, {"type": "SPORT"}),
        "/sports-bademode-herren/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/sportschuhe-herren/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/sports-herren-rucksack/": (ProductCategory.BACKPACK.value, {"type": "SPORT"}),
        "/sports-herren-taschen/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/herrenschuhe-sneaker/": ProductCategory.SNEAKERS.value,
        "/herrenschuhe-schnuerer/": ProductCategory.SHOES.value,
        "/herrenschuhe-halbschuhe/": ProductCategory.SHOES.value,
        "/herrenschuhe-business-schuhe/": ProductCategory.SHOES.value,
        "/herrenschuhe-offene-schuhe/": ProductCategory.SHOES.value,
        "/herrenschuhe-boots/": ProductCategory.SHOES.value,
        "/herrenschuhe-hausschuhe/": ProductCategory.SHOES.value,
        "/taschen-accessoires-taschen-herren/": ProductCategory.BAG.value,
        "/rucksaecke-herren/": ProductCategory.BACKPACK.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def female() -> List[dict]:
    path_2_category = {
        "/damenbekleidung-kleider/": ProductCategory.DRESS.value,
        "/t-shirts-kurzarm/": ProductCategory.TSHIRT.value,
        "/damenbekleidung-tops/": ProductCategory.SHIRT.value,
        "/damenbekleidung-shirts-poloshirts/": ProductCategory.SHIRT.value,
        "/langarmshirt/": ProductCategory.TSHIRT.value,
        "/damenbekleidung-blusen-tuniken/": ProductCategory.BLOUSE.value,
        "/damenbekleidung-pullover-sweater-strickpullover/": ProductCategory.SWEATER.value,
        "/damenbekleidung-strickjacken/": ProductCategory.JACKET.value,
        "/damenbekleidung-sweatshirts-hoodies/": ProductCategory.SWEATER.value,
        "/damenbekleidung-jacken/": ProductCategory.JACKET.value,
        "/damenbekleidung-jacken-maentel/": ProductCategory.JACKET.value,
        "/damenbekleidung-jeans/": ProductCategory.JEANS.value,
        "/damenbekleidung-hosen/": ProductCategory.PANTS.value,
        "/damenbekleidung-hosen-shorts/": ProductCategory.PANTS.value,
        "/damenbekleidung-hosen-overalls-jumpsuit/": ProductCategory.OVERALL.value,
        "/damenbekleidung-roecke/": ProductCategory.SKIRT.value,
        "/damenbekleidung-waesche/": ProductCategory.UNDERWEAR.value,
        "/nachtwaesche/": ProductCategory.NIGHTWEAR.value,
        "/damenbekleidung-struempfe/": ProductCategory.SOCKS.value,
        "/damenbekleidung-bademode/": ProductCategory.SWIMWEAR.value,
        "/sports-damen-shirts-funktion/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sports-poloshirts-damen/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-top-damen/": (ProductCategory.TOP.value, {"type": "SPORT"}),
        "/sports-langarmshirts-damen/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "/sports-blusen-damen/": (ProductCategory.BLOUSE.value, {"type": "SPORT"}),
        "/sports-damen-shirts-trikot/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "/sports-jacken-damen/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "/sporthosen-damen/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "/sports-damen-pullover-sweater/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "/sports-kleider-roecke/": (ProductCategory.DRESS.value, {"type": "SPORT"}),
        "/sport-bh/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/funktionsunterwaesche-damen/": (ProductCategory.UNDERWEAR.value, {"type": "SPORT"}),
        "/sports-damen-struempfe/": (ProductCategory.SOCKS.value, {"type": "SPORT"}),
        "/sportanzuege-damen/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "/sports-bademode-damen/": (ProductCategory.SWIMWEAR.value, {"type": "SPORT"}),
        "/sportschuhe-damen/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "/sports-rucksack-damen/": (ProductCategory.BACKPACK.value, {"type": "SPORT"}),
        "/sports-taschen-damen/": (ProductCategory.BAG.value, {"type": "SPORT"}),
        "/damenschuhe-sneaker/": ProductCategory.SNEAKERS.value,
        "/damenschuhe-stiefeletten/": ProductCategory.SHOES.value,
        "/damenschuhe-stiefel/": ProductCategory.SHOES.value,
        "/damenschuhe-sandaletten/": ProductCategory.SHOES.value,
        "/damenschuhe-high-heels/": ProductCategory.SHOES.value,
        "/damenschuhe-pumps/": ProductCategory.SHOES.value,
        "/damenschuhe-brautschuhe/": ProductCategory.SHOES.value,
        "/flache-schuhe/": ProductCategory.SHOES.value,
        "/damenschuhe-ballerinas/": ProductCategory.SHOES.value,
        "/damenschuhe-pantoletten/": ProductCategory.SHOES.value,
        "/damenschuhe-hausschuhe/": ProductCategory.SHOES.value,
        "/damenschuhe-badeschuhe/": ProductCategory.SHOES.value,
        "/taschen-accessoires-taschen-damen/": ProductCategory.BAG.value,
        "/rucksaecke/": ProductCategory.BACKPACK.value,
    }

    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )


def get_settings() -> List[dict]:
    return male() + female()
