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
                "start_urls": f"https://www.amazon.de/s?bbn={node}&rh=n%3A{node}%2Cp_n_cpf_eligible%3A22579885031",  # noqa
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps(metadata),
            }
        )
    return results


def female() -> List[dict]:
    node_2_category = {
        "1760314031": ProductCategory.SHOES.value,
        "1760307031": ProductCategory.SHOES.value,
        "17302968031": ProductCategory.SHOES.value,
        "1760309031": ProductCategory.SHOES.value,
        "17302980031": ProductCategory.SHOES.value,
        "17507763031": ProductCategory.SNEAKERS.value,
        "1760365031": ProductCategory.SHOES.value,
        "1981723031": ProductCategory.JEANS.value,
        "1981838031": ProductCategory.SKIRT.value,
        "1981874031": ProductCategory.PANTS.value,
        "1981721031": ProductCategory.DRESS.value,
        "1760237031": ProductCategory.BAG.value,
        "1981872031": ProductCategory.TSHIRT.value,
        "1981873031": ProductCategory.TOP.value,
        "1981871031": ProductCategory.SHIRT.value,
        "1981870031": ProductCategory.TSHIRT.value,
        "1981720031": ProductCategory.BLOUSE.value,
        "1981825031": ProductCategory.NIGHTWEAR.value,
        "1981725031": ProductCategory.SWEATER.value,
        "1981724031": ProductCategory.OVERALL.value,
        "1981733031": ProductCategory.UNDERWEAR.value,
        "1981835031": ProductCategory.JACKET.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def male() -> List[dict]:
    node_2_category = {
        "1760374031": ProductCategory.SHOES.value,
        "1760369031": ProductCategory.SHOES.value,
        "1760371031": ProductCategory.SHOES.value,
        "1760372031": ProductCategory.SHOES.value,
        "17507802031": ProductCategory.SNEAKERS.value,
        "1760425031": ProductCategory.SHOES.value,
        "1760426031": ProductCategory.SHOES.value,
        "1981350031": ProductCategory.JEANS.value,
        "1981391031": ProductCategory.SWIMWEAR.value,
        "1981399031": ProductCategory.PANTS.value,
        "195940011": ProductCategory.BACKPACK.value,
        "1981398031": ProductCategory.TOP.value,
        "1981397031": ProductCategory.TSHIRT.value,
        "1981396031": ProductCategory.SHIRT.value,
        "1981395031": ProductCategory.TSHIRT.value,
        "1981368031": ProductCategory.SHIRT.value,
        "1981369031": ProductCategory.SHIRT.value,
        "1981370031": ProductCategory.SHIRT.value,
        "1981356031": ProductCategory.NIGHTWEAR.value,
        "1981351031": ProductCategory.SWEATER.value,
        "1981400031": ProductCategory.UNDERWEAR.value,
        "1981365031": ProductCategory.JACKET.value,
    }

    return combine_results(
        node_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def electronics() -> List[dict]:
    node_2_category = {
        "427957031": ProductCategory.LAPTOP.value,
        "429874031": ProductCategory.TABLET.value,
        "570278": ProductCategory.HEADPHONES.value,
        "427955031": ProductCategory.PRINTER.value,
    }

    return combine_results(
        node_2_category,
        metadata={"family": "electronics"},
    )


def get_settings() -> List[dict]:
    return male() + female() + electronics()
