import json
from typing import List

from core.domain import ConsumerLifestageType, GenderType, ProductCategory

SUSTAINABILITY_FILTER = "?nachhaltigkeit=beruecksichtigt-tierwohl,energieeffiziente-nutzung,foerderung-sozialer-initiativen,kreislauffaehiges-design,materialien-aus-biologischem-anbau,naturkosmetik,recycelte-materialien,verbesserte-herstellung,verbesserte-rohstoffbeschaffung"  # noqa


def clothes_and_shoes() -> List[dict]:
    base_path = "https://www.otto.de"
    filter = SUSTAINABILITY_FILTER

    sex_to_path = {GenderType.MALE.value: "herren", GenderType.FEMALE.value: "damen"}

    path_2_category = {
        "arbeitskleidung/arbeitsschuhe/": ProductCategory.SHOES.value,
        "fahrraeder/fahrradbekleidung/fahrradhosen/": ProductCategory.PANTS.value,
        "fahrraeder/fahrradbekleidung/fahrradjacken/": ProductCategory.JACKET.value,
        "fahrraeder/fahrradbekleidung/fahrradschuhe/": ProductCategory.SHOES.value,
        "fahrraeder/fahrradbekleidung/fahrradtrikots/": ProductCategory.SHIRT.value,
        "kraftraeder/schutzkleidung/motorradhosen/": ProductCategory.PANTS.value,
        "kraftraeder/schutzkleidung/motorradjacken/": ProductCategory.JACKET.value,
        "kraftraeder/schutzkleidung/motorradstiefel/": ProductCategory.SHOES.value,
        "mode/anzuege/": ProductCategory.SUIT.value,
        "mode/bademode/": ProductCategory.SWIMWEAR.value,
        "mode/blazer/": ProductCategory.JACKET.value,
        "mode/blusen/": ProductCategory.BLOUSE.value,
        "mode/hemden/": ProductCategory.SHIRT.value,
        "mode/hosen/": ProductCategory.PANTS.value,
        "mode/hosen/jeans/": ProductCategory.JEANS.value,
        # has some subcategories that should be in NIGHTWEAR
        # same for mode/shirts/
        "mode/jacken/": ProductCategory.JACKET.value,
        "mode/kleider/": ProductCategory.DRESS.value,
        "mode/maentel/": ProductCategory.JACKET.value,
        "mode/overalls/": ProductCategory.OVERALL.value,
        "mode/pullover/": ProductCategory.SWEATER.value,
        "mode/roecke/": ProductCategory.SKIRT.value,
        "mode/sakkos/": ProductCategory.JACKET.value,
        "mode/schuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/sneaker/": ProductCategory.SNEAKERS.value,
        "mode/schuhe/ballerinas/": ProductCategory.SHOES.value,
        "mode/schuhe/boots/": ProductCategory.SHOES.value,
        "mode/schuhe/business-schuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/clogs/": ProductCategory.SHOES.value,
        "mode/schuhe/gummistiefel/": ProductCategory.SHOES.value,
        "mode/schuhe/halbschuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/hausschuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/high-heels/": ProductCategory.SHOES.value,
        "mode/schuhe/outdoorschuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/pumps/": ProductCategory.SHOES.value,
        "mode/schuhe/sandalen/": ProductCategory.SHOES.value,
        "mode/schuhe/sicherheitsschuhe/": ProductCategory.SHOES.value,
        "mode/schuhe/stiefel/": ProductCategory.SHOES.value,
        "mode/schuhe/stiefeletten/": ProductCategory.SHOES.value,
        "mode/shirts/": ProductCategory.SHIRT.value,
        "mode/shirts/t-shirts/": ProductCategory.TSHIRT.value,
        "mode/strickjacken/": ProductCategory.JACKET.value,
        "mode/tops/": ProductCategory.TOP.value,
        "mode/tuniken/": ProductCategory.BLOUSE.value,
        "mode/waesche/bhs/": ProductCategory.UNDERWEAR.value,
        "mode/waesche/morgenmaentel/": ProductCategory.NIGHTWEAR.value,
        "mode/waesche/nachthemden/": ProductCategory.NIGHTWEAR.value,
        "mode/waesche/nachtwaesche-sets/": ProductCategory.NIGHTWEAR.value,
        "mode/waesche/pyjamas/": ProductCategory.NIGHTWEAR.value,
        "mode/waesche/socken/": ProductCategory.SOCKS.value,
        "mode/waesche/struempfe/": ProductCategory.SOCKS.value,
        "mode/waesche/strumpfhosen/": ProductCategory.UNDERWEAR.value,
        "mode/waesche/unterhemden/": ProductCategory.UNDERWEAR.value,
        "mode/waesche/unterhosen/": ProductCategory.UNDERWEAR.value,
        "mode/waesche/unterkleider/": ProductCategory.UNDERWEAR.value,
        "mode/westen/": ProductCategory.JACKET.value,
        "mode/sportmode/sportschuhe/": (ProductCategory.SNEAKERS.value, {"type": "SPORT"}),
        "mode/sportmode/sportschuhe/badeschuhe/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "mode/sportmode/sportschuhe/reitstiefel/": (ProductCategory.SHOES.value, {"type": "SPORT"}),
        "mode/sportmode/sportschuhe/reitstiefeletten/": (
            ProductCategory.SHOES.value,
            {"type": "SPORT"},
        ),
        "mode/sportmode/sportanzuege/": (ProductCategory.TRACKSUIT.value, {"type": "SPORT"}),
        "mode/sportmode/sportshirts/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "mode/sportmode/sportshirts/t-shirts/": (ProductCategory.TSHIRT.value, {"type": "SPORT"}),
        "mode/sportmode/trikots/": (ProductCategory.SHIRT.value, {"type": "SPORT"}),
        "mode/sportmode/funktionsblusen/": (ProductCategory.BLOUSE.value, {"type": "SPORT"}),
        "mode/sportmode/funktionswaesche/thermoleggings/": (
            ProductCategory.PANTS.value,
            {"type": "SPORT"},
        ),
        "mode/sportmode/sporthosen/": (ProductCategory.PANTS.value, {"type": "SPORT"}),
        "mode/sportmode/sportjacken/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
        "mode/sportmode/sportkleider/": (ProductCategory.DRESS.value, {"type": "SPORT"}),
        "mode/sportmode/sportpullover/": (ProductCategory.SWEATER.value, {"type": "SPORT"}),
        "mode/sportmode/sportroecke/": (ProductCategory.SKIRT.value, {"type": "SPORT"}),
        "mode/sportmode/sporttops/": (ProductCategory.TOP.value, {"type": "SPORT"}),
        "mode/sportmode/sportwesten/": (ProductCategory.JACKET.value, {"type": "SPORT"}),
    }

    results = []
    for sex, sex_path in sex_to_path.items():
        for path, category in path_2_category.items():
            results.append(
                {
                    "start_urls": f"{base_path}/{path}{filter}&zielgruppe={sex_path}",
                    "category": category,
                    "gender": sex,
                    "consumer_lifestage": ConsumerLifestageType.ADULT.value,
                    "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
                }
            )
    return results


def bags() -> List[dict]:
    base_path = "https://www.otto.de"
    filter = SUSTAINABILITY_FILTER

    sex_to_path = {GenderType.MALE.value: "herren", GenderType.FEMALE.value: "damen"}

    results = []
    for sex, path in sex_to_path.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/taschen/rucksaecke/{filter}",
                "category": ProductCategory.BACKPACK.value,
                "gender": sex,
                "consumer_lifestage": ConsumerLifestageType.ADULT.value,
                "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
            }
        )
        results.append(
            {
                "start_urls": f"{base_path}/{path}/taschen/{filter}",
                "category": ProductCategory.BAG.value,
                "gender": sex,
                "consumer_lifestage": ConsumerLifestageType.ADULT.value,
                "meta_data": json.dumps({"sex": sex, "family": "FASHION"}),
            }
        )
    return results


def electronics() -> List[dict]:
    base_path = "https://www.otto.de/technik"
    # For the need of more products and externally matched labels (EM),
    # we're not filtering for sustainable products only, thus the filter is empty.
    filter = ""

    path_2_category = {
        "smartphone": ProductCategory.SMARTPHONE.value,
        "laptop": ProductCategory.LAPTOP.value,
        "tablet": ProductCategory.TABLET.value,
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"family": "electronics"}),
            }
        )
    return results


def textiles() -> List[dict]:
    base_path = "https://www.otto.de/heimtextilien"
    filter = SUSTAINABILITY_FILTER

    path_2_category = {
        "handtuecher": ProductCategory.TOWEL.value,
        "bettwaesche": ProductCategory.LINEN.value,
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"family": "textiles"}),
            }
        )
    return results


def household() -> List[dict]:
    base_path = "https://www.otto.de/haushalt"
    filter = SUSTAINABILITY_FILTER

    path_2_category = {
        "backoefen": ProductCategory.OVEN.value,
        "dunstabzugshauben": ProductCategory.COOKER_HOOD.value,
        "gefrierschraenke": ProductCategory.FREEZER.value,
        "geschirrspueler": ProductCategory.DISHWASHER.value,
        "herde": ProductCategory.STOVE.value,
        "kuehlschraenke": ProductCategory.FRIDGE.value,
        "trockner": ProductCategory.DRYER.value,
        "waschmaschinen": ProductCategory.WASHER.value,
    }

    results = []
    for path, category in path_2_category.items():
        results.append(
            {
                "start_urls": f"{base_path}/{path}/{filter}",
                "category": category,
                "meta_data": json.dumps({"family": "electronics"}),
            }
        )
    return results


def get_settings() -> List[dict]:
    return clothes_and_shoes() + bags() + textiles() + household() + electronics()
