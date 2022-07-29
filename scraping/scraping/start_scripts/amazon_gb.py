import json
from typing import List, Optional

from core.domain import ConsumerLifestageType, GenderType, ProductCategory


def combine_results(
    node_2_category: dict,
    metadata: dict,
    gender: Optional[str] = None,
    consumer_lifestage: Optional[str] = None,
) -> List[dict]:
    results = []
    for node, category in node_2_category.items():
        results.append(
            {
                "start_urls": f"https://www.amazon.co.uk/s?bbn={node}&rh=n%3A{node}%2Cp_n_cpf_eligible%3A22579929031",  # noqa
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps(metadata),
            }
        )
    return results


def female() -> List[dict]:
    node_2_category = {
        "1769849031": ProductCategory.SHOES.value,
        "1769850031": ProductCategory.SHOES.value,
        "1769851031": ProductCategory.SHOES.value,
        "17516503031": ProductCategory.SNEAKERS.value,
        "17302930031": ProductCategory.SHOES.value,
        "1769858031": ProductCategory.SHOES.value,
        "1769857031": ProductCategory.SHOES.value,
        "1731353031": ProductCategory.JEANS.value,
        "1731468031": ProductCategory.SKIRT.value,
        "1731504031": ProductCategory.PANTS.value,
        "1731351031": ProductCategory.DRESS.value,
        "1769559031": ProductCategory.BAG.value,
        "1731502031": ProductCategory.TSHIRT.value,
        "1731500031": ProductCategory.SHIRT.value,
        "1731503031": ProductCategory.SHIRT.value,
        "1731350031": ProductCategory.BLOUSE.value,
        "1731455031": ProductCategory.NIGHTWEAR.value,
        "1731355031": ProductCategory.SWEATER.value,
        "1731363031": ProductCategory.UNDERWEAR.value,
        "1731474031": ProductCategory.SOCKS.value,
        "1731462031": ProductCategory.JACKET.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def male() -> List[dict]:
    node_2_category = {
        "1769554031": ProductCategory.BAG.value,
        "1769788031": ProductCategory.SHOES.value,
        "1769789031": ProductCategory.SHOES.value,
        "17516504031": ProductCategory.SNEAKERS.value,
        "1769792031": ProductCategory.SHOES.value,
        "1769793031": ProductCategory.SHOES.value,
        "1769795031": ProductCategory.SHOES.value,
        "1769794031": ProductCategory.SHOES.value,
        "1730982031": ProductCategory.SWEATER.value,
        "1731008031": ProductCategory.SOCKS.value,
        "1730981031": ProductCategory.JEANS.value,
        "1731030031": ProductCategory.PANTS.value,
        "1731028031": ProductCategory.TSHIRT.value,
        "1731027031": ProductCategory.SHIRT.value,
        "1730998031": ProductCategory.SHIRT.value,
        "1730987031": ProductCategory.NIGHTWEAR.value,
        "1731031031": ProductCategory.UNDERWEAR.value,
        "1730993031": ProductCategory.JACKET.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def electronics() -> List[dict]:
    node_2_category = {
        "4085731": ProductCategory.HEADPHONES.value,
        "429886031": ProductCategory.LAPTOP.value,
        "428653031": ProductCategory.PRINTER.value,
        "356496011": ProductCategory.SMARTPHONE.value,
        "3457450031": ProductCategory.SMARTWATCH.value,
        "429892031": ProductCategory.TABLET.value,
        "560864": ProductCategory.TV.value,
    }

    return combine_results(node_2_category, metadata={"family": "electronics"})


def household() -> List[dict]:
    node_2_category = {
        "1391011031": ProductCategory.COOKER_HOOD.value,
        "10706491": ProductCategory.DISHWASHER.value,
        "1391019031": ProductCategory.DRYER.value,
        "10706351": ProductCategory.FREEZER.value,
        "13528548031": ProductCategory.FRIDGE.value,
        "3229376031": ProductCategory.LINEN.value,
        "1391013031": ProductCategory.OVEN.value,
        "1391010031": ProductCategory.STOVE.value,
        "11712721": ProductCategory.TOWEL.value,
        "3618681": ProductCategory.WASHER.value,
    }

    return combine_results(node_2_category, metadata={"family": "electronics"})


def get_settings() -> List[dict]:
    return male() + female() + electronics() + household()
