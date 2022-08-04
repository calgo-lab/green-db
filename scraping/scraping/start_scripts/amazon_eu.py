import json
import pkgutil

# from bisect import bisect_left
from typing import Any, List, Optional, Tuple

from core.domain import ConsumerLifestageType, GenderType


# use bisect.bisect_left if we ever update to 3.10
# on python 3.9 bisect_left lacks the `key` argument
def bisect_left(a: list, x: Any, key: Any) -> int:
    low = 0
    high = len(a)
    while low < high:
        mid = (low + high) // 2
        if key(a[mid]) < x:
            low = mid + 1
        else:
            high = mid
    return low


def read_json(path: str) -> list:
    data = pkgutil.get_data("scraping", path)
    assert data
    return json.loads(data.decode("utf-8"))


sort_key = "{root}{path}/".format_map
browse_tree_leaves = sorted(read_json("data/amazon_eu_browse_nodes.json"), key=sort_key)

# unfortunately the json file only contains leaf nodes
# so we have to do some extra work to map a browse node path to its leaf nodes.
# we wouldnt need to do any of this if we had an amazon.json which contained internal nodes aswell.


def find_leaf_nodes_by_path(path: str) -> Tuple[int, int]:
    """
    find all leaf nodes matching a given path

    Args:
        path (str): the name of some amazon browse node

    Returns:
        Tuple[int, int]: the range of leaf nodes given as (length, offset)
    """
    seperator = "/"
    assert not path.startswith(seperator) and not path.endswith(seperator)
    one_after_seperator = chr(ord(seperator) + 1)
    start = bisect_left(browse_tree_leaves, path + seperator, key=sort_key)
    end = bisect_left(browse_tree_leaves, path + one_after_seperator, key=sort_key)
    return end - start, start


def translate_paths_in_category_map(path_2_category: dict) -> dict:
    """
    replaces each path in a category mapping with its corresponding leaf nodes.
    here its more convenient to refer to a leaf node by its index.

    Args:
        path_2_category (dict): a map from paths to categories

    Returns:
        dict: a map from leaf node indices to categories
    """

    ranges = sorted(
        (*find_leaf_nodes_by_path(browse_node), category)
        for browse_node, category in path_2_category.items()
    )

    index_2_category = {}

    for length, offset, category in reversed(ranges):
        for i in range(offset, offset + length):
            index_2_category[i] = category

    return index_2_category


def combine_results(
    country_code: str,
    path_2_category: dict,
    metadata: dict,
    gender: Optional[str] = None,
    consumer_lifestage: Optional[str] = None,
) -> List[dict]:

    country_code_to_url = {
        "fr": "https://www.amazon.fr",
        "de": "https://www.amazon.de",
        "uk": "https://www.amazon.co.uk",
        "it": "https://www.amazon.it",
        "es": "https://www.amazon.es",
    }

    base_url = country_code_to_url[country_code]

    index_2_category = translate_paths_in_category_map(path_2_category)

    results = []
    for i, category in index_2_category.items():
        if category:
            node = browse_tree_leaves[i]["id"][country_code]
            assert node & 1
            results.append(
                {
                    "start_urls": f"{base_url}/s?bbn={node}&rh=n%3A{node}%2Cp_n_cpf_eligible%3A22579881031",  # noqa
                    "category": category,
                    "gender": gender,
                    "consumer_lifestage": consumer_lifestage,
                    "meta_data": json.dumps(metadata),
                }
            )
    return results


def female(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-apparel/Categories/Women/Blouses & Shirts": "BLOUSE",
        "uk-apparel/Categories/Women/Coats & Jackets": "JACKETS",
        "uk-apparel/Categories/Women/Dresses": "DRESS",
        "uk-apparel/Categories/Women/Dungarees": "OVERALL",
        "uk-apparel/Categories/Women/Hoodies": "SWEATER",
        "uk-apparel/Categories/Women/Jeans": "JEANS",
        "uk-apparel/Categories/Women/Jumpsuits & Playsuits": "OVERALL",
        "uk-apparel/Categories/Women/Knitwear/Cardigans": "JACKET",
        "uk-apparel/Categories/Women/Knitwear/Jumpers": "SWEATER",
        "uk-apparel/Categories/Women/Knitwear/Ponchos & Capes": None,
        "uk-apparel/Categories/Women/Knitwear/Shrugs": None,
        "uk-apparel/Categories/Women/Knitwear/Tank Tops": "TOP",
        "uk-apparel/Categories/Women/Knitwear/Twin-Sets": None,
        "uk-apparel/Categories/Women/Leggings": "PANTS",
        "uk-apparel/Categories/Women/Lingerie & Underwear": "UNDERWEAR",
        "uk-apparel/Categories/Women/Lingerie & Underwear/Accessories": None,
        "uk-apparel/Categories/Women/Nightwear": "NIGHTWEAR",
        "uk-apparel/Categories/Women/Shorts": "PANTS",
        "uk-apparel/Categories/Women/Skirts": "SKIRT",
        "uk-apparel/Categories/Women/Socks & Tights": "SOCKS",
        "uk-apparel/Categories/Women/Sportswear/Athletic Socks": ("SOCKS", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Base Layers": ("UNDERWEAR", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Dresses": ("DRESS", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Gilets": ("JACKET", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Knickers & Bras": ("UNDERWEAR", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Knitwear": None,
        "uk-apparel/Categories/Women/Sportswear/Shirts & Tees": ("SHIRT", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Shorts": ("PANTS", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Skirts": ("SKIRT", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Tights & Leggings": ("SOCKS", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Track Jackets": ("JACKET", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Tracksuits": ("TRACKSUIT", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Sportswear/Trousers": ("PANTS", {"type": "SPORT"}),
        "uk-apparel/Categories/Women/Suits & Blazers": "SUIT",
        "uk-apparel/Categories/Women/Suits & Blazers/Suit Jackets & Blazers": "JACKET",
        "uk-apparel/Categories/Women/Sweatshirts": "SWEATER",
        "uk-apparel/Categories/Women/Swimwear": "SWIMWEAR",
        "uk-apparel/Categories/Women/Tops & T-Shirts": "TOP",
        "uk-apparel/Categories/Women/Tops & T-Shirts/Polos": "SHIRT",
        "uk-apparel/Categories/Women/Tops & T-Shirts/T-Shirts": "TSHIRT",
        "uk-apparel/Categories/Women/Trousers": "PANTS",
    }

    return combine_results(
        country_code,
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def male(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-apparel/Categories/Men/Knitwear/Cardigans": "JACKET",
        "uk-apparel/Categories/Men/Knitwear/Gilets": "JACKET",
        "uk-apparel/Categories/Men/Knitwear/Jumpers": "SWEATER",
        "uk-apparel/Categories/Men/Knitwear/Tank Tops": "TOP",
        "uk-apparel/Categories/Men/Nightwear": "NIGHTWEAR",
        "uk-apparel/Categories/Men/Coats & Jackets": "JACKET",
        "uk-apparel/Categories/Men/Dungarees": "OVERALL",
        "uk-apparel/Categories/Men/Hoodies": "SWEATER",
        "uk-apparel/Categories/Men/Jeans": "JEANS",
        "uk-apparel/Categories/Men/Shirts": "SHIRT",
        "uk-apparel/Categories/Men/Shorts": "PANTS",
        "uk-apparel/Categories/Men/Socks": "SOCKS",
        "uk-apparel/Categories/Men/Sportswear/Athletic Socks": ("SOCKS", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Base Layers": ("UNDERWEAR", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Gilets": ("JACKET", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Knitwear": None,
        "uk-apparel/Categories/Men/Sportswear/Shirts & Tees": ("SHIRT", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Shorts": ("PANTS", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Tights & Leggings": ("PANTS", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Track Jackets": ("JACKET", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Tracksuits": ("TRACKSUIT", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Trousers": ("PANTS", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Sportswear/Underwear": ("UNDERWEAR", {"type": "SPORT"}),
        "uk-apparel/Categories/Men/Suits & Blazers": "SUIT",
        "uk-apparel/Categories/Men/Suits & Blazers/Blazers": "JACKET",
        "uk-apparel/Categories/Men/Suits & Blazers/Suit Jackets": "JACKET",
        "uk-apparel/Categories/Men/Suits & Blazers/Suit Trousers": "PANTS",
        "uk-apparel/Categories/Men/Suits & Blazers/Tuxedo Jackets": "JACKET",
        "uk-apparel/Categories/Men/Suits & Blazers/Tuxedo Trousers": "PANTS",
        "uk-apparel/Categories/Men/Sweatshirts": "SWEATER",
        "uk-apparel/Categories/Men/Swimwear": "SWIMWEAR",
        "uk-apparel/Categories/Men/Tops & T-Shirts": "SHIRT",
        "uk-apparel/Categories/Men/Tops & T-Shirts/T-Shirts": "TSHIRT",
        "uk-apparel/Categories/Men/Trousers": "PANTS",
        "uk-apparel/Categories/Men/Underwear": "UNDERWEAR",
    }

    return combine_results(
        country_code,
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
        metadata={"family": "FASHION"},
    )


def electronics(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-computers/Products/Ink & Laser Printers": "PRINTER",
        "uk-computers/Products/Ink & Laser Printers/Plotters": None,
        "uk-computers/Products/Laptops": "LAPTOP",
        "uk-computers/Products/Tablets": "TABLET",
        "uk-computers/Products/Webcams & VoIP Equipment/PC Headsets": "HEADPHONES",
        "uk-electronics/Categories/Accessories/Home Audio & Video Accessories/Headphones & Earphones": "HEADPHONES",  # noqa
        "uk-electronics/Categories/Home Cinema, TV & Video/TVs": "TV",
        "uk-electronics/Categories/Mobile Phones & Communication/Big Button Mobile Phones": None,
        "uk-electronics/Categories/Mobile Phones & Communication/Mobile Phones & Smartphones": "SMARTPHONE",  # noqa
        "uk-electronics/Categories/Mobile Phones & Communication/Smartwatches": "SMARTWATCH",
    }

    return combine_results(
        country_code,
        path_2_category,
        metadata={"family": "electronics"},
    )


def household(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-appliances/Categories/Combined Ovens & Hobs": "STOVE",
        "uk-appliances/Categories/Dishwashers": "DISHWASHER",
        "uk-appliances/Categories/Freezers": "FREEZER",
        "uk-appliances/Categories/Fridge-freezers": "FRIDGE",
        "uk-appliances/Categories/Fridges": "FRIDGE",
        "uk-appliances/Categories/Hobs": None,
        "uk-appliances/Categories/Installed Ovens": "OVEN",
        "uk-appliances/Categories/Mini Freezers": None,
        "uk-appliances/Categories/Mini Fridges": None,
        "uk-appliances/Categories/Ovens": "OVEN",
        "uk-appliances/Categories/Range Cookers": "STOVE",
        "uk-appliances/Categories/Range Cooktops": None,
        "uk-appliances/Categories/Vent Hoods": "COOKER_HOOD",
        "uk-appliances/Categories/Washing Machines & Tumble Dryers/Dryers": "DRYER",
        "uk-appliances/Categories/Washing Machines & Tumble Dryers/Spin Dryers": "DRYER",
        "uk-appliances/Categories/Washing Machines & Tumble Dryers/Stacked Washers & Dryers": None,
        "uk-appliances/Categories/Washing Machines & Tumble Dryers/Washer-Dryers": "WASHER",
        "uk-appliances/Categories/Washing Machines & Tumble Dryers/Washing Machines": "WASHER",
    }

    return combine_results(country_code, path_2_category, metadata={"family": "electronics"})


def get_settings(country_code: str) -> List[dict]:
    return (
        male(country_code)
        + female(country_code)
        + electronics(country_code)
        + household(country_code)
    )
