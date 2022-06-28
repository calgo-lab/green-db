import json
from typing import List


def combine_results(
    node_2_category: dict,
    metadata: dict,
) -> List[dict]:
    results = []
    for node, category in node_2_category.items():
        results.append(
            {
                "start_urls": f"https://www.amazon.co.uk/s?bbn={node}&rh=n%3A{node}%2Cp_n_cpf_eligible%3A22579929031",  # noqa
                "category": category,
                "meta_data": json.dumps(metadata),
            }
        )
    return results


def female() -> List[dict]:
    node_2_category = {
        "1769798031": "SHOES",
        "1731353031": "JEANS",
        "1731468031": "SKIRT",
        "1731504031": "PANT",
        "1731351031": "DRESS",
        "1769551031": "BAG",
        "1731502031": "TOP",
        "1731503031": "TOP",
        "1731350031": "BLOUSE",
        "1731455031": "NIGHTWEAR",
        "14704067031": "SWEATER",
        "1731363031": "UNDERWEAR",
        "1731462031": "JACKET",
    }

    return combine_results(node_2_category, metadata={"family": "FASHION", "sex": "FEMALE"})


def male() -> List[dict]:
    node_2_category = {
        "1769738031": "SHOES",
        "1730981031": "JEANS",
        "1731030031": "PANT",
        "1731028031": "TOP",
        "1731027031": "TOP",
        "1730998031": "SHIRT",
        "1730987031": "NIGHTWEAR",
        "1730983031": "SWEATER",
        "14704068031": "SWEATER",
        "1730985031": "SWEATER",
        "1731031031": "UNDERWEAR",
        "1730993031": "JACKET",
    }

    return combine_results(node_2_category, metadata={"family": "FASHION", "sex": "MALE"})


def electronics() -> List[dict]:
    node_2_category = {
        "429886031": "LAPTOP",
        "429892031": "TABLET",
        "4085731": "HEADPHONES",
        "428653031": "PRINTER",
    }

    return combine_results(node_2_category, metadata={"family": "electronics"})


def get_settings() -> List[dict]:
    return male() + female() + electronics()
