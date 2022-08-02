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
                "start_urls": f"https://www.amazon.fr/s?bbn={node}&rh=n%3A{node}%2Cp_n_cpf_eligible%3A22579881031",  # noqa
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps(metadata),
            }
        )
    return results


def female() -> List[dict]:
    node_2_category = {
        "17507815031": ProductCategory.SNEAKERS.value,
        "1765059031": ProductCategory.SHOES.value,
        "1765060031": ProductCategory.SHOES.value,
        "1765063031": ProductCategory.SHOES.value,
        "17303004031": ProductCategory.SHOES.value,
        "1765112031": ProductCategory.SHOES.value,
        "1765115031": ProductCategory.SHOES.value,
        "1765116031": ProductCategory.SHOES.value,
        "17303005031": ProductCategory.SHOES.value,
        "464670031": ProductCategory.JEANS.value,
        "464674031": ProductCategory.SKIRT.value,
        "464671031": ProductCategory.PANTS.value,
        "464668031": ProductCategory.DRESS.value,
        "1765336031": ProductCategory.BAG.value,
        "464645031": ProductCategory.BLOUSE.value,
        "464643031": ProductCategory.TOP.value,
        "464644031": ProductCategory.SHIRT.value,
        "464642031": ProductCategory.TSHIRT.value,
        "2308721031": ProductCategory.TSHIRT.value,
        "464699031": ProductCategory.NIGHTWEAR.value,
        "464646031": ProductCategory.SWEATER.value,
        "464669031": ProductCategory.OVERALL.value,
        "464709031": ProductCategory.UNDERWEAR.value,
        "464682031": ProductCategory.JACKET.value,
        "464748031": ProductCategory.SWIMWEAR.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def male() -> List[dict]:
    node_2_category = {
        "17507816031": ProductCategory.SNEAKERS.value,
        "1765044031": ProductCategory.SHOES.value,
        "1765045031": ProductCategory.SHOES.value,
        "1765047031": ProductCategory.SHOES.value,
        "1765055031": ProductCategory.SHOES.value,
        "1765290031": ProductCategory.SHOES.value,
        "1765291031": ProductCategory.SHOES.value,
        "1765292031": ProductCategory.SHOES.value,
        "1765046031": ProductCategory.SHOES.value,
        "1765293031": ProductCategory.SHOES.value,
        "1765294031": ProductCategory.SHOES.value,
        "464841031": ProductCategory.JEANS.value,
        "464843031": ProductCategory.PANTS.value,
        "464842031": ProductCategory.PANTS.value,
        "1765350031": ProductCategory.BAG.value,
        "464828031": ProductCategory.SHIRT.value,
        "513435031": ProductCategory.TOP.value,
        "464807031": ProductCategory.SHIRT.value,
        "464806031": ProductCategory.TSHIRT.value,
        "2308845031": ProductCategory.TSHIRT.value,
        "464810031": ProductCategory.NIGHTWEAR.value,
        "464823031": ProductCategory.SWEATER.value,
        "464861031": ProductCategory.UNDERWEAR.value,
        "464849031": ProductCategory.JACKET.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def electronics() -> List[dict]:
    node_2_category = {
        "682942031": ProductCategory.HEADPHONES.value,
        "429879031": ProductCategory.LAPTOP.value,
        "17414953031": ProductCategory.PRINTER.value,
        "218193031": ProductCategory.SMARTPHONE.value,
        "3457486031": ProductCategory.SMARTWATCH.value,
        "429882031": ProductCategory.TABLET.value,
        "14059871": ProductCategory.TV.value,
    }

    return combine_results(
        node_2_category,
        metadata={"family": "electronics"},
    )


def household() -> List[dict]:
    node_2_category = {
        "57856031": ProductCategory.COOKER_HOOD.value,
        "57847031": ProductCategory.DISHWASHER.value,
        "57851031": ProductCategory.DRYER.value,
        "57854031": ProductCategory.FREEZER.value,
        "11633389031": ProductCategory.FRIDGE.value,
        "22217684031": ProductCategory.LINEN.value,
        "1332681031": ProductCategory.OVEN.value,
        "58786031": ProductCategory.STOVE.value,
        "3196894031": ProductCategory.TOWEL.value,
        "57849031": ProductCategory.WASHER.value,
    }

    return combine_results(node_2_category, metadata={"family": "electronics"})


def get_settings() -> List[dict]:
    return male() + female() + electronics() + household()
