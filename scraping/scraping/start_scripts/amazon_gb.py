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
        "1769798031": ProductCategory.SHOES.value,
        "1731353031": ProductCategory.JEANS.value,
        "1731468031": ProductCategory.SKIRT.value,
        "1731504031": ProductCategory.PANTS.value,
        "1731351031": ProductCategory.DRESS.value,
        "1769551031": ProductCategory.BAG.value,
        "1731502031": ProductCategory.TOP.value,
        "1731503031": ProductCategory.TOP.value,
        "1731350031": ProductCategory.BLOUSE.value,
        "1731455031": ProductCategory.NIGHTWEAR.value,
        "14704067031": ProductCategory.SWEATER.value,
        "1731363031": ProductCategory.UNDERWEAR.value,
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
        "1769738031": ProductCategory.SHOES.value,
        "1730981031": ProductCategory.JEANS.value,
        "1731030031": ProductCategory.PANTS.value,
        "1731028031": ProductCategory.TOP.value,
        "1731027031": ProductCategory.TOP.value,
        "1730998031": ProductCategory.SHIRT.value,
        "1730987031": ProductCategory.NIGHTWEAR.value,
        "1730983031": ProductCategory.SWEATER.value,
        "14704068031": ProductCategory.SWEATER.value,
        "1730985031": ProductCategory.SWEATER.value,
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
        "429886031": ProductCategory.LAPTOP,
        "429892031": ProductCategory.TABLET,
        "4085731": ProductCategory.HEADPHONES,
        "428653031": ProductCategory.PRINTER,
    }

    return combine_results(node_2_category, metadata={"family": "electronics"})


def get_settings() -> List[dict]:
    return male() + female() + electronics()
