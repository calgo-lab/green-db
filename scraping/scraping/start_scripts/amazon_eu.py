import json
import pkgutil
from logging import getLogger

# from bisect import bisect_left
from typing import Any, List, Optional, Tuple

from core.domain import ConsumerLifestageType, GenderType, ProductCategory

logger = getLogger(__name__)


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
# we wouldnt need to do that if we had a list of internal nodes aswell.


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
    replaces each path in a category mapping with the corresponding leaf nodes.
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
    }

    country_code_to_filters = {
        "fr": "p_n_cpf_eligible%3A22579881031",
        "de": "p_n_cpf_eligible%3A22579885031",
        "uk": "p_n_cpf_eligible%3A22579929031",
    }

    base_url = country_code_to_url[country_code]
    filters = country_code_to_filters[country_code]

    index_2_category = translate_paths_in_category_map(path_2_category)

    results = []
    for i, category in index_2_category.items():
        if category:
            if node := browse_tree_leaves[i]["id"][country_code]:
                results.append(
                    {
                        "start_urls": f"{base_url}/s?bbn={node}&rh=n%3A{node}%2C{filters}",
                        "category": category,
                        "gender": gender,
                        "consumer_lifestage": consumer_lifestage,
                        "meta_data": json.dumps(metadata),
                    }
                )
    return results


def female(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-apparel/Categories/Women/Blouses & Shirts": ProductCategory.BLOUSE.value,
        "uk-apparel/Categories/Women/Coats & Jackets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Dresses": ProductCategory.DRESS.value,
        "uk-apparel/Categories/Women/Dungarees": ProductCategory.OVERALL.value,
        "uk-apparel/Categories/Women/Hoodies": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Women/Jeans": ProductCategory.JEANS.value,
        "uk-apparel/Categories/Women/Jumpsuits & Playsuits": ProductCategory.OVERALL.value,
        "uk-apparel/Categories/Women/Knitwear/Cardigans": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Knitwear/Jumpers": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Women/Knitwear/Ponchos & Capes": None,
        "uk-apparel/Categories/Women/Knitwear/Shrugs": None,
        "uk-apparel/Categories/Women/Knitwear/Tank Tops": ProductCategory.TOP.value,
        "uk-apparel/Categories/Women/Knitwear/Twin-Sets": None,
        "uk-apparel/Categories/Women/Leggings": ProductCategory.PANTS.value,
        "uk-apparel/Categories/Women/Lingerie & Underwear": ProductCategory.UNDERWEAR.value,
        "uk-apparel/Categories/Women/Lingerie & Underwear/Accessories": None,
        "uk-apparel/Categories/Women/Nightwear": ProductCategory.NIGHTWEAR.value,
        "uk-apparel/Categories/Women/Shorts": ProductCategory.SHORTS.value,
        "uk-apparel/Categories/Women/Skirts": ProductCategory.SKIRT.value,
        "uk-apparel/Categories/Women/Socks & Tights": ProductCategory.SOCKS.value,
        "uk-apparel/Categories/Women/Socks & Tights/Tights": ProductCategory.UNDERWEAR.value,
        "uk-apparel/Categories/Women/Sportswear/Athletic Socks": (
            ProductCategory.SOCKS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Base Layers": (
            ProductCategory.UNDERWEAR.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Dresses": (
            ProductCategory.DRESS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Gilets": (
            ProductCategory.JACKET.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Knickers & Bras": (
            ProductCategory.UNDERWEAR.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Knitwear": None,
        "uk-apparel/Categories/Women/Sportswear/Shirts & Tees": (
            ProductCategory.SHIRT.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Shorts": (
            ProductCategory.SHORTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Skirts": (
            ProductCategory.SKIRT.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Tights & Leggings": (
            ProductCategory.PANTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Track Jackets": (
            ProductCategory.JACKET.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Tracksuits": (
            ProductCategory.TRACKSUIT.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Sportswear/Trousers": (
            ProductCategory.PANTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Women/Suits & Blazers": ProductCategory.SUIT.value,
        "uk-apparel/Categories/Women/Suits & Blazers/Suit Jackets & Blazers": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Suits & Blazers/Waistcoats": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Sweatshirts": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Women/Swimwear": ProductCategory.SWIMWEAR.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts": ProductCategory.TOP.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts/Polos": ProductCategory.SHIRT.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts/T-Shirts": ProductCategory.TSHIRT.value,
        "uk-apparel/Categories/Women/Trousers": ProductCategory.PANTS.value,
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
        "uk-apparel/Categories/Men/Knitwear/Cardigans": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Knitwear/Gilets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Knitwear/Jumpers": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Men/Knitwear/Tank Tops": ProductCategory.TOP.value,
        "uk-apparel/Categories/Men/Nightwear": ProductCategory.NIGHTWEAR.value,
        "uk-apparel/Categories/Men/Coats & Jackets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Dungarees": ProductCategory.OVERALL.value,
        "uk-apparel/Categories/Men/Hoodies": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Men/Jeans": ProductCategory.JEANS.value,
        "uk-apparel/Categories/Men/Shirts": ProductCategory.SHIRT.value,
        "uk-apparel/Categories/Men/Shorts": ProductCategory.SHORTS.value,
        "uk-apparel/Categories/Men/Socks": ProductCategory.SOCKS.value,
        "uk-apparel/Categories/Men/Sportswear/Athletic Socks": (
            ProductCategory.SOCKS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Base Layers": (
            ProductCategory.UNDERWEAR.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Gilets": (
            ProductCategory.JACKET.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Knitwear": None,
        "uk-apparel/Categories/Men/Sportswear/Shirts & Tees": (
            ProductCategory.SHIRT.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Shorts": (
            ProductCategory.SHORTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Tights & Leggings": (
            ProductCategory.PANTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Track Jackets": (
            ProductCategory.JACKET.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Tracksuits": (
            ProductCategory.TRACKSUIT.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Trousers": (
            ProductCategory.PANTS.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Sportswear/Underwear": (
            ProductCategory.UNDERWEAR.value,
            {"type": "SPORT"},
        ),
        "uk-apparel/Categories/Men/Suits & Blazers": ProductCategory.SUIT.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Blazers": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Suit Jackets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Suit Trousers": ProductCategory.PANTS.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Tuxedo Jackets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Tuxedo Trousers": ProductCategory.PANTS.value,
        "uk-apparel/Categories/Men/Suits & Blazers/Waistcoats": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Men/Sweatshirts": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Men/Swimwear": ProductCategory.SWIMWEAR.value,
        "uk-apparel/Categories/Men/Tops & T-Shirts": ProductCategory.TOP.value,
        "uk-apparel/Categories/Men/Tops & T-Shirts/Polos": ProductCategory.SHIRT.value,
        "uk-apparel/Categories/Men/Tops & T-Shirts/T-Shirts": ProductCategory.TSHIRT.value,
        "uk-apparel/Categories/Men/Trousers": ProductCategory.PANTS.value,
        "uk-apparel/Categories/Men/Underwear": ProductCategory.UNDERWEAR.value,
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
        "uk-computers/Products/Ink & Laser Printers": ProductCategory.PRINTER.value,
        "uk-computers/Products/Ink & Laser Printers/Plotters": None,
        "uk-computers/Products/Laptops": ProductCategory.LAPTOP.value,
        "uk-computers/Products/Tablets": ProductCategory.TABLET.value,
        "uk-computers/Products/Webcams & VoIP Equipment/PC Headsets": ProductCategory.HEADPHONES.value,
        "uk-electronics/Categories/Accessories/Home Audio & Video Accessories/Headphones & Earphones": ProductCategory.HEADPHONES.value,  # noqa
        "uk-electronics/Categories/Home Cinema, TV & Video/TVs": ProductCategory.TV.value,
        "uk-electronics/Categories/Mobile Phones & Communication/Big Button Mobile Phones": None,
        "uk-electronics/Categories/Mobile Phones & Communication/Mobile Phones & Smartphones": ProductCategory.SMARTPHONE.value,  # noqa
        "uk-electronics/Categories/Mobile Phones & Communication/Smartwatches": ProductCategory.SMARTWATCH.value,
    }

    return combine_results(
        country_code,
        path_2_category,
        metadata={"family": "electronics"},
    )


def household(country_code: str) -> List[dict]:
    path_2_category = {
        "de-appliances/Kategorien/Geschirrspüler": ProductCategory.DISHWASHER.value,
        "de-appliances/Kategorien/Herde": ProductCategory.STOVE.value,
        "fr-appliances/Catégories/Congélateurs": ProductCategory.FREEZER.value,
        "fr-appliances/Catégories/Fours avec commandes pour Tables de cuisson": ProductCategory.OVEN.value,
        "fr-appliances/Catégories/Lave-linge et Sèche-linge": ProductCategory.WASHER.value,
        "fr-appliances/Catégories/Lave-linge et Sèche-linge/Essoreuses": ProductCategory.DRYER.value,
        "fr-appliances/Catégories/Lave-linge et Sèche-linge/Sèche-linges": ProductCategory.DRYER.value,
        "fr-appliances/Catégories/Réfrigérateurs": ProductCategory.FRIDGE.value,
        "fr-appliances/Catégories/Fours encastrables": ProductCategory.OVEN.value,
        "fr-appliances/Catégories/Hottes aspirantes": ProductCategory.COOKER_HOOD.value,
    }

    return combine_results(country_code, path_2_category, metadata={"family": "electronics"})


def get_settings(country_code: str) -> List[dict]:
    return (
        male(country_code)
        + female(country_code)
        + electronics(country_code)
        + household(country_code)
    )
