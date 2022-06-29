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
        "1760304031": "SHOES",
        "1981723031": "JEANS",
        "1981838031": "SKIRT",
        "1981874031": "PANT",
        "1981721031": "DRESS",
        "1760237031": "BAG",
        "1981872031": "TOP",
        "1981873031": "TOP",
        "1981871031": "TOP",
        "1981870031": "TOP",
        "1981720031": "BLOUSE",
        "1981825031": "NIGHTWEAR",
        "1981725031": "SWEATER",
        "1981724031": "OVERALL",
        "1981733031": "UNDERWEAR",
        "1981835031": "JACKET",
    }

    return combine_results(
        node_2_category, gender="FEMALE", consumer_lifestage="ADULT", metadata={"family": "FASHION"}
    )


def male() -> List[dict]:
    node_2_category = {
        "1760367031": "SHOES",
        "1981350031": "JEANS",
        "1981391031": "SWIMMWEAR",
        "1981399031": "PANT",
        "195940011": "BACKPACK",
        "1981398031": "TOP",
        "1981397031": "TOP",
        "1981396031": "TOP",
        "1981395031": "TOP",
        "1981368031": "SHIRT",
        "1981369031": "SHIRT",
        "1981370031": "SHIRT",
        "1981356031": "NIGHTWEAR",
        "1981351031": "SWEATER",
        "1981400031": "UNDERWEAR",
        "1981365031": "JACKET",
    }

    return combine_results(
        node_2_category, gender="MALE", consumer_lifestage="ADULT", metadata={"family": "FASHION"}
    )


def electronics() -> List[dict]:
    node_2_category = {
        "427957031": "LAPTOP",
        "429874031": "TABLET",
        "570278": "HEADPHONES",
        "427955031": "PRINTER",
    }

    return combine_results(
        node_2_category,
        metadata={"family": "electronics"},
    )


def get_settings() -> List[dict]:
    return male() + female() + electronics()
