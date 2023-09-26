import json
from typing import List

from core.domain import ConsumerLifestageType, GenderType, ProductCategory


def combine_results(
    path_2_category: dict,
    gender: str,
    consumer_lifestage: str,
) -> List[dict]:
    results = []
    for path, info in path_2_category.items():
        category, meta_data = info if type(info) == tuple else (info, {})
        results.append(
            {
                "start_urls": f"https://www.avocadostore.de{path}?criteria[]=careful_use_of_resources&criteria[]=co2_neutral&criteria[]=cradle_to_cradle&criteria[]=durable&criteria[]=eco&criteria[]=fair&criteria[]=made_in_germany&criteria[]=pollutants_reduced_production&criteria[]=recycled&criteria[]=vegan",
                "category": category,
                "gender": gender,
                "consumer_lifestage": consumer_lifestage,
                "meta_data": json.dumps({"family": "FASHION", **meta_data}),
            }
        )
    return results


def male() -> List[dict]:
    path_2_category = {
        "/herren/t-shirts": ProductCategory.TSHIRT,
        "/herren/hemden": ProductCategory.SHIRT,
        "/herren/hosen": ProductCategory.PANTS,
        "/herren/chinos": ProductCategory.PANTS,
        "/herren/lange-hosen": ProductCategory.PANTS,
        "/herren/shorts": ProductCategory.SHORTS,
        "/herren/leinenhosen": ProductCategory.PANTS,
        "/herren/cordhosen": ProductCategory.PANTS,
        "/herren/jogginghosen": ProductCategory.PANTS,
        "/herren/jeans": ProductCategory.JEANS,
        "/herren/pullover": ProductCategory.SWEATER,
        "/herren/sweatshirts-hoodies": ProductCategory.SWEATER,
        "/herren/jacken": ProductCategory.JACKET,
        "/herren/maentel": ProductCategory.JACKET,
        "/herren/waesche": ProductCategory.UNDERWEAR,
        "/herren/socken": ProductCategory.SOCKS,
        "/herren/oberteile": (ProductCategory.SHIRT, {"type": "SPORT"}),
        "/herren/sportbekleidung-unterteile": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/herren/bademode": ProductCategory.SWIMWEAR,
        "/herren/sneaker": ProductCategory.SNEAKERS,
        "/herren/schnuerschuhe": ProductCategory.SHOES,
        "/herren/schuhe-sportschuhe": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/herren/slipper": ProductCategory.SHOES,
        "/herren/business-schuhe": ProductCategory.SHOES,
        "/herren/schuhe-casual": ProductCategory.SHOES,
        "/herren/sandalen": ProductCategory.SHOES,
        "/herren/stiefel": ProductCategory.SHOES,
        "/herren/hausschuhe": ProductCategory.SHOES,
        "/herren/barfussschuhe": ProductCategory.SHOES,
        "/herren/flip-flops": ProductCategory.SHOES,
        "/herren/badeschuhe": ProductCategory.SHOES,
        "/herren/schuhe-vegan": ProductCategory.SHOES,
        "/herren/clogs": ProductCategory.SHOES,
        "/herren/schuhe-gummistiefel": ProductCategory.SHOES,
        "/herren/schuhe-berufsschuhe": ProductCategory.SHOES,
        "/herren/taschen": ProductCategory.BAG,
        "/herren/taschen/rucksaecke": ProductCategory.BACKPACK,
        "/herren/yoga/kleidung-tank-tops": ProductCategory.SHIRT,
        "/herren/yoga/kleidung-yogashirts": ProductCategory.SHIRT,
        "/herren/yoga/kleidung-yogahosen": ProductCategory.PANTS,
    }
    return combine_results(
        path_2_category,
        gender=GenderType.MALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )

def female() -> List[dict]:
    path_2_category = {
        "/damen/kleider": ProductCategory.DRESS,
        "/damen/shirts": ProductCategory.SHIRT,
        "/damen/tops": ProductCategory.TOP,
        "/damen/blusen-tuniken": ProductCategory.BLOUSE,
        "/damen/jeans": ProductCategory.JEANS,
        "/damen/hosen-chinos": ProductCategory.PANTS,
        "/damen/stoffhosen": ProductCategory.PANTS,
        "/damen/cordhosen": ProductCategory.PANTS,
        "/damen/lange-hosen": ProductCategory.PANTS,
        "/damen/shorts": ProductCategory.SHORTS,
        "/damen/leggings": ProductCategory.PANTS,
        "/damen/culottes": ProductCategory.PANTS,
        "/damen/jogginghosen": ProductCategory.PANTS,
        "/damen/wohlfuehlhose": ProductCategory.PANTS,
        "/damen/latzhosen": ProductCategory.PANTS,
        "/damen/pullover": ProductCategory.SWEATER,
        "/damen/sweatshirts-hoodies": ProductCategory.SWEATER,
        "/damen/jacken": ProductCategory.JACKET,
        "/damen/mantel": ProductCategory.JACKET,
        "/damen/roecke": ProductCategory.SKIRT,
        "/damen/jumpsuits": ProductCategory.OVERALL,
        "/damen/waesche": ProductCategory.UNDERWEAR,
        "/damen/socken-und-strumpfhosen": ProductCategory.SOCKS,
        "/damen/sportbekleidung-oberteile": (ProductCategory.TOP, {"type": "SPORT"}),
        "/damen/sportbekleidung-unterteile": (ProductCategory.PANTS, {"type": "SPORT"}),
        "/damen/bademode": ProductCategory.SWIMWEAR,
        "/damen/sneaker": ProductCategory.SNEAKERS,
        "/damen/stiefeletten": ProductCategory.SHOES,
        "/damen/sandalen": ProductCategory.SHOES,
        "/damen/halbschuhe": ProductCategory.SHOES,
        "/damen/ballerinas": ProductCategory.SHOES,
        "/damen/schuhe-sportschuhe": (ProductCategory.SHOES, {"type": "SPORT"}),
        "/damen/hohe-schuhe": ProductCategory.SHOES,
        "/damen/flache-schuhe": ProductCategory.SHOES,
        "/damen/espadrilles": ProductCategory.SHOES,
        "/damen/pantoletten": ProductCategory.SHOES,
        "/damen/sandaletten": ProductCategory.SHOES,
        "/damen/hausschuhe": ProductCategory.SHOES,
        "/damen/pumps": ProductCategory.SHOES,
        "/damen/stiefel": ProductCategory.SHOES,
        "/damen/schnuerschuhe": ProductCategory.SHOES,
        "/damen/barfussschuhe": ProductCategory.SHOES,
        "/damen/flip-flops": ProductCategory.SHOES,
        "/damen/clogs": ProductCategory.SHOES,
        "/damen/schuhe-vegan": ProductCategory.SHOES,
        "/damen/schuhe-gummistiefel": ProductCategory.SHOES,
        "/damen/schuhe-berufsschuhe": ProductCategory.SHOES,
        "/damen/yoga-tops": ProductCategory.TOP,
        "/yoga/damen-yogahosen": ProductCategory.PANTS,
        "/yoga/damen-yoga-leggings": ProductCategory.PANTS,
        "/yoga/damen-yogashirts": ProductCategory.SHIRT,
        "/yoga/damen-yoga-bh": ProductCategory.UNDERWEAR,
        "/damen/yoga/kleidung-tops": ProductCategory.TOP,
        "/damen/yoga/kleidung-shirts": ProductCategory.SHIRT,
        "/damen/yoga/kleidung-leggings": ProductCategory.PANTS,
        "/damen/yoga/kleidung-yogahosen": ProductCategory.PANTS,
        "/damen/yoga/kleidung-yoga-bh": ProductCategory.UNDERWEAR,
    }
    return combine_results(
        path_2_category,
        gender=GenderType.FEMALE.value,
        consumer_lifestage=ConsumerLifestageType.ADULT.value,
    )




