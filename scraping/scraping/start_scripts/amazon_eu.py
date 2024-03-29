import json
from collections import defaultdict
from logging import getLogger
from typing import List, Optional

from core.domain import ConsumerLifestageType, GenderType, ProductCategory
from scraping.utils import get_json_data

logger = getLogger(__name__)

browse_tree_leaves = get_json_data("amazon_eu_browse_nodes.json")
path_2_leaves_builder = defaultdict(list)

# unfortunately the json file only contains leaf nodes
# so we have to do some extra work to map a browse node path to its leaf nodes.
# we wouldnt need to do that if we had a list of internal nodes aswell.

for leaf in browse_tree_leaves:
    path = "{root}{path}".format_map(leaf)
    split_path = path.split("/")
    for i in range(len(split_path)):
        subpath = "/".join(split_path[: i + 1])
        path_2_leaves_builder[subpath].append(leaf)

path_2_leaves = dict(path_2_leaves_builder)


def replace_paths_in_category_map(path_2_category: dict, country_code: str) -> dict:
    """
    replaces paths in a category mapping with the corresponding browse node ids.
    in cases where path_2_category is ambiguous, the most specific mapping will win.

    for example  replace_paths_in_category_map({"a/b/c": "PANTS", "a/b/c/d": "DISWASHER"})

    will map all children of "a/b/c" to "PANTS" except those which are
    also children of "a/b/c/d" which will be mapped to "DISHWASHER"

    Args:
        path_2_category (dict): a map from paths to categories
        country_code (str): one of "uk", "de" or "fr"

    Returns:
        dict: a map from browse node ids to categories
    """

    id_2_category = {}

    for path in sorted(path_2_category, key=len):
        category = path_2_category[path]
        for leaf in path_2_leaves[path]:
            id_2_category[leaf["id"][country_code]] = category

    return id_2_category


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

    id_2_category = replace_paths_in_category_map(path_2_category, country_code)

    return [
        {
            "start_urls": f"{base_url}/s?bbn={node}&rh=n%3A{node}%2C{filters}",
            "category": category,
            "gender": gender,
            "consumer_lifestage": consumer_lifestage,
            "meta_data": json.dumps(metadata),
        }
        for node, category in id_2_category.items()
        if node and category
    ]


def female(country_code: str) -> List[dict]:
    path_2_category = {
        "uk-apparel/Categories/Women/Blouses & Shirts": ProductCategory.BLOUSE.value,
        "uk-apparel/Categories/Women/Coats & Jackets": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Dresses": ProductCategory.DRESS.value,
        "uk-apparel/Categories/Women/Dungarees": ProductCategory.PANTS.value,
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
        "uk-apparel/Categories/Women/Suits & Blazers/Suit Jackets & Blazers": ProductCategory.JACKET.value,  # noqa
        "uk-apparel/Categories/Women/Suits & Blazers/Waistcoats": ProductCategory.JACKET.value,
        "uk-apparel/Categories/Women/Sweatshirts": ProductCategory.SWEATER.value,
        "uk-apparel/Categories/Women/Swimwear": ProductCategory.SWIMWEAR.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts": ProductCategory.SHIRT.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts/T-Shirts": ProductCategory.TSHIRT.value,
        "uk-apparel/Categories/Women/Tops & T-Shirts/Vest Tops": ProductCategory.TOP.value,
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
        "uk-apparel/Categories/Men/Dungarees": ProductCategory.PANTS.value,
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
        "uk-apparel/Categories/Men/Tops & T-Shirts": ProductCategory.SHIRT.value,
        "uk-apparel/Categories/Men/Tops & T-Shirts/Vests": ProductCategory.TOP.value,
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
        "uk-computers/Products/Webcams & VoIP Equipment/PC Headsets": ProductCategory.HEADSET.value,  # noqa
        "uk-electronics/Categories/Accessories/Home Audio & Video Accessories/Headphones & Earphones": ProductCategory.HEADPHONES.value,  # noqa
        "uk-electronics/Categories/Home Cinema, TV & Video/TVs": ProductCategory.TV.value,
        "uk-electronics/Categories/Mobile Phones & Communication/Big Button Mobile Phones": None,
        "uk-electronics/Categories/Mobile Phones & Communication/Mobile Phones & Smartphones": ProductCategory.SMARTPHONE.value,  # noqa
        "uk-electronics/Categories/Mobile Phones & Communication/Smartwatches": ProductCategory.SMARTWATCH.value,  # noqa
    }

    return combine_results(
        country_code,
        path_2_category,
        metadata={"family": "electronics"},
    )


def household(country_code: str) -> List[dict]:
    path_2_category = {
        # the mappings in uk-appliances are wrong and incomplete so i used de/fr root nodes here.
        "de-appliances/Kategorien/Geschirrspüler": ProductCategory.DISHWASHER.value,
        "de-appliances/Kategorien/Herde": ProductCategory.STOVE.value,
        "fr-appliances/Catégories/Congélateurs": ProductCategory.FREEZER.value,
        "fr-appliances/Catégories/Fours avec commandes pour Tables de cuisson": ProductCategory.OVEN.value,  # noqa
        "fr-appliances/Catégories/Lave-linge et Sèche-linge": ProductCategory.WASHER.value,
        "fr-appliances/Catégories/Lave-linge et Sèche-linge/Essoreuses": ProductCategory.DRYER.value,  # noqa
        "fr-appliances/Catégories/Lave-linge et Sèche-linge/Sèche-linges": ProductCategory.DRYER.value,  # noqa
        "fr-appliances/Catégories/Réfrigérateurs": ProductCategory.FRIDGE.value,
        "fr-appliances/Catégories/Fours encastrables": ProductCategory.OVEN.value,
        "fr-appliances/Catégories/Hottes aspirantes": ProductCategory.COOKER_HOOD.value,
    }

    return combine_results(country_code, path_2_category, metadata={"family": "electronics"})


def get_settings(country_code: str) -> List[dict]:
    return (
        electronics(country_code)
        + male(country_code)
        + female(country_code)
        + household(country_code)
    )
