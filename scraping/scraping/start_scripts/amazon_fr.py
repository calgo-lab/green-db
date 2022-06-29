import json
from typing import List, Optional


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
        "1765056031": "SHOES",
        "464670031": "JEANS",
        "464674031": "SKIRT",
        "464671031": "PANT",
        "464668031": "DRESS",
        "1765336031": "BAG",
        "464641031": "TOP",
        "464699031": "NIGHTWEAR",
        "464646031": "SWEATER",
        "464669031": "OVERALL",
        "464709031": "UNDERWEAR",
        "464682031": "JACKET",
        "464748031": "SWIMMWEAR",
    }

    return combine_results(
        node_2_category,
        gender="FEMALE",
        consumer_lifestage="ADULT",
        metadata={"family": "FASHION"},
    )


def male() -> List[dict]:
    node_2_category = {
        "1765241031": "SHOES",
        "464841031": "JEANS",
        "464843031": "SHORTS",
        "464842031": "PANT",
        "1765350031": "BAG",
        "464828031": "SHIRT",
        "464805031": "TSHIRT",
        "464810031": "NIGHTWEAR",
        "464823031": "SWEATER",
        "464861031": "UNDERWEAR",
        "464849031": "JACKET",
    }

    return combine_results(
        node_2_category,
        gender="MALE",
        consumer_lifestage="ADULT",
        metadata={"family": "FASHION"},
    )


def electronics() -> List[dict]:
    node_2_category = {
        "429879031": "LAPTOP",
        "429882031": "TABLET",
        "682942031": "HEADPHONES",
        "17414953031": "PRINTER",
    }

    return combine_results(
        node_2_category,
        metadata={"family": "electronics"},
    )


def get_settings() -> List[dict]:
    return male() + female() + electronics()
