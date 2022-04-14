import json
from typing import Dict, List, Tuple, Union


def combine_results(
    path_2_category: dict,
    sex: str,    
) -> List[dict]:
    results = []
    for path, category in path_2_category.items():
        print(path, category, sex)
        results.append(
            {
                "start_urls": f"https://www.amazon.de/s?bbn={path}&rh=n%3A{path}%2Cp_n_cpf_eligible%3A22579885031",             
                "category": category,
                "meta_data": {"familiy": "FASHION", "sex": sex},                
            }
        )
        print(results)
    return results


def female() -> List[dict]:
    path_2_category = {
        "1760365031": "SHOES"
    }

    return combine_results(path_2_category, sex="FEMALE")


def male() -> List[dict]:
    path_2_category = {
        "1981350031": "SHOES",
        "1760425031": "JEANS"
    }

    return combine_results(path_2_category, sex="MALE")


def get_settings() -> List[dict]:
    return male() + female()