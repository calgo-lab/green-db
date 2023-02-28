import json
import re
from html import escape
from math import exp, log
from random import random, seed
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plots
from minify_html import minify
from plotly import graph_objects as go
from plotly.io import to_html
from plotly.offline import get_plotlyjs
from sqlalchemy import desc, func, literal_column, or_
from utils import Element, render_markdown, render_page, render_tag

from core.constants import ALL_SCRAPING_TABLE_NAMES
from core.domain import Product, ProductCategory
from core.sustainability_labels.bootstrap_database import sustainability_labels
from database.connection import GreenDB, Scraping

label_map = {label.id: label for label in sustainability_labels}
js_label_info = json.dumps(
    {
        label.id: {
            k: 0 if v is None else v
            for k, v in label.dict().items()
            if k not in {"id", "timestamp"}
        }
        for label in sustainability_labels
    }
)
label_metrics = [
    ("label_cred_credibility", "cred_credibility"),
    ("label_eco_chemicals", "eco_chemicals"),
    ("label_eco_lifetime", "eco_lifetime"),
    ("label_eco_water", "eco_water"),
    ("label_eco_inputs", "eco_inputs"),
    ("label_eco_quality", "eco_quality"),
    ("label_eco_energy", "eco_energy"),
    ("label_eco_waste_air", "eco_waste_air"),
    ("label_eco_environmental_management", "eco_environmental_management"),
    ("label_social_labour_rights", "social_labour_rights"),
    ("label_social_business_practice", "social_business_practice"),
    ("label_social_social_rights", "social_social_rights"),
    ("label_social_company_responsibility", "social_company_responsibility"),
    ("label_social_conflict_minerals", "social_conflict_minerals"),
]

category_typos = {"PANT": "PANTS", "SHORT": "SHORTS", "JEAN": "JEANS", "SWIMMWEAR": "SWIMWEAR"}


def to_linear(srgb: float) -> float:
    if srgb < 0:
        return 0
    if srgb > 1:
        return 1
    if srgb < 0.04045:
        return srgb / 12.92
    return pow((srgb + 0.055) / 1.055, 2.4)


def to_srgb(linear: float) -> float:
    if linear < 0:
        return 0
    if linear > 1:
        return 1
    if linear < 0.0031308:
        return linear * 12.92
    return pow(linear, 1.0 / 2.4) * 1.055 - 0.055


def kurgel(p: float, q: float) -> float:
    if q == 0:
        return 0
    s = p / q
    return 1 + s - (s * s + 2 * s) ** 0.5


def shadow(bg: float, fg: float, s: float = 0.5, p: float = 0.62) -> float:
    return bg * s / (1.0 - p * bg * fg)


def bevel(bg: float, fg: float, s: float, p: float = 0.62) -> float:
    return fg + shadow(bg, fg, s, p)


def medium(a: float, t: float) -> float:
    return 1 / (t * (1 - a) + 1)


def blend(a: float, b: float, t: float) -> float:
    return (1 - t) ** 2 * a / (1 - t * a * b) + t * b


def temp2color(temp: float) -> List[float]:
    if temp == 0:
        return [0, 0, 0]
    return [f**3 / (exp(f / temp) - 1 + log(10) * 30) / 5 for f in [26, 30, 35]]


def map(func: Any, *iterables: Any, **kwargs: Any) -> Any:
    return (func(*args, **kwargs) for args in zip(*iterables))


def webcolor(color: List[float]) -> str:
    return "#" + "".join(f"{round(to_srgb(c)*255):02x}" for c in color)


def linspace(start: float, end: float, n: int) -> List[float]:
    return [start + (end - start) * i / (n - 1) for i in range(n)]


def animate(curve: list) -> List[Tuple[int, Any]]:
    return [(i * 100 // (len(curve) - 1), c) for i, c in enumerate(curve)]


def render_plotly_figure(
    fig: Any, width: Any = "100%", height: Any = "100%", div_id: Optional[str] = None
) -> str:
    return to_html(
        fig,
        config={"staticPlot": True},
        include_plotlyjs=False,
        full_html=False,
        default_width=width,
        default_height=height,
        div_id=div_id,
    )


def render_table_entry(entry: Any) -> str:
    if entry is None:
        return ""
    if isinstance(entry, list):
        return ", ".join(map(render_table_entry, entry))
    return str(entry)


def render_table(names: List[str], rows: List[list]) -> str:
    table = "\n".join(" | ".join(map(render_table_entry, row)) for row in rows)
    return render_markdown(f"|{' | '.join(names)}|\n|{' | '.join('-' for i in names)}|\n|{table}|")


def render_dataframe(df: pd.DataFrame) -> str:
    return render_table([*df], df.values)


product_table_attribs = ["name", "category", "brand", "labels", "price", "currency"]
seed(1)
label_cred_tint = [blend(kurgel(random() * 6, random()), 0.05, 0.1) for i in range(3)]
label_eco_tint = [blend(kurgel(random() * 6, random()), 0.05, 0.1) for i in range(3)]
label_social_tint = [blend(kurgel(random() * 6, random()), 0.05, 0.1) for i in range(3)]
label_eco_tint = [blend(kurgel(random() * 6, random()), 0.05, 0.1) for i in range(3)]
label_eco_tint = [blend(kurgel(random() * 6, random()), 0.05, 0.1) for i in range(3)]
label_colors = {}


def render_label(label: str) -> str:
    label_text = re.sub(r"^certificate:", "", label)
    label_info = label_map[label]
    cred = label_info.cred_credibility or 0
    seed(label + "1")
    tint = [kurgel(random() * 4, random()) for i in range(3)]
    color = [1 if cred >= 50 else 0.5] * 3
    idle = [blend(t, 0.05, 1 - cred / 100) for t in tint]
    seed(11)
    hover = [blend(t, medium(random(), 50), .2) for t in idle]
    label_colors[label_text] = (color, idle, hover)
    assert " " not in label_text, label_text
    return render_tag(
        "div",
        None,
        ["label", label_text],
        label_text,
        [
            f'onclick="focusLabel(event, {repr(label)})"',
        ],
    )


def product2dict(product: Product) -> dict:
    replacements = dict(
        labels=" ".join(render_label(label) for label in product.sustainability_labels),
        category=category_typos.get(product.category, product.category),
    )
    return {
        key: replacements.get(key, None) or getattr(product, key) for key in product_table_attribs
    }


def render_products(products: List[Product], n: int = 5) -> str:

    dicts = [product2dict(product) for product in products]

    optional = [True, False, True, False, True, True]
    attribs = ["name", "category", "brand", "labels", "price", "currency"]
    rows = [[product[attr] for attr in attribs] for product in dicts]
    urls = [escape(product.url) for product in products]

    head = render_tag(
        "div",
        None,
        ["table-row"],
        "".join(
            render_tag("div", None, ["optional"] * o + ["table-header"], attrib)
            for attrib, o in zip(attribs, optional)
        ),
    )

    body = [
        render_tag(
            "a",
            None,
            ["table-row", "product-link"],
            "".join(
                render_tag(
                    "div", None, ["optional"] * o + ["table-cell"], render_table_entry(entry)
                )
                for entry, o in zip(row, optional)
            ),
            [f'href="{url}"'],
        )
        for i, (url, row) in enumerate(zip(urls, rows))
    ]

    return render_tag(
        "div",
        None,
        ["table"],
        render_tag("div", None, ["hidden"], "".join(body[n:])) + head + "".join(body[:n]),
    )


def render_excerpt(products: List[Product]) -> str:
    script = """
    event.target.disabled = true;
    setTimeout(function() {{
        const stuff = event.target.parentNode.getElementsByClassName("hidden")[0];
        const table = stuff.parentNode;
        for(var i = 0; i < 4 && stuff.childNodes.length > 0; i++) {{
            const k = Math.floor(Math.random() * stuff.childNodes.length);
            table.appendChild(stuff.childNodes[k]);
        }}
        event.target.disabled = stuff.childNodes.length == 0;
    }}, 400);
    """

    return f'<div class="excerpt"><div class="table-wrapper">{render_products(products)}</div><button class="btn" onclick="{escape(script)}">more</button></div>'  # noqa


def similarity(a: set, b: set) -> float:
    return len(a & b) / (len(a) * len(b))


def filter_products(products: List[Product], count: int) -> List[Product]:
    products = [
        p
        for p in products
        if len("".join(p.sustainability_labels)) < 50 + len(p.sustainability_labels) * 4
    ]
    if count >= len(products):
        return products
    selected = [0]
    not_selected = set(range(1, len(products)))
    vecs = [{p.brand, *p.sustainability_labels} for p in products]
    for _ in range(1, count):
        idx = min(not_selected, key=lambda i: max(similarity(vecs[i], vecs[j]) for j in selected))
        not_selected.remove(idx)
        selected.append(idx)
    return [products[i] for i in selected]


def get_relevant_products(
    self: GreenDB, count: int, credibility_threshold: int = 50
) -> List[Product]:
    """
    Fetch `count` products at random.

    Yields:
        Iterator[Product]: `Iterator` of domain object representation
    """
    timestamp = self.get_latest_timestamp()
    with self._session_factory() as db_session:
        labels = self.get_sustainability_labels_subquery()
        get_credible_labels = (
            db_session.query(labels.c.id)
            .filter(labels.c.cred_credibility >= credibility_threshold)
            .all()
        )
        credible_labels = [label[0] for label in get_credible_labels]
        query = (
            db_session.query(self._database_class)
            .filter(self._database_class.timestamp == timestamp)
            .filter(
                or_(
                    *[
                        self._database_class.sustainability_labels.any(label)
                        for label in credible_labels
                    ]
                )
            )
            .filter(func.length(self._database_class.name) < 50)
            .order_by(func.random())
        )
        return [Product.from_orm(row) for row in query.limit(count).all()]


def get_eco_soc_rank_by_sustainability(self: GreenDB, aggregated_by: str) -> pd.DataFrame:
    """
    This function ranks unique credible products by its aggregated sustainability score.

    Args:
        aggregated_by (str): Determines product attribute to aggregated data.

    Returns:
        pd.DataFrame: Query results as `pd.Dataframe`.
    """
    with self._session_factory() as db_session:
        unique_credible_products = self.calculate_sustainability_scores()

        aggregation_map = {
            "merchant": self._database_class.merchant,
            "category": self._database_class.category,
            "brand": self._database_class.brand,
        }

        return pd.DataFrame(
            db_session.query(
                aggregation_map[aggregated_by],
                func.round(func.avg(unique_credible_products.c.sustainability_score)).label(
                    "sustainability_score"
                ),
                func.round(func.avg(unique_credible_products.c.ecological_score)).label(
                    "ecological_score"
                ),
                func.round(func.avg(unique_credible_products.c.social_score)).label("social_score"),
            )
            .join(
                unique_credible_products,
                unique_credible_products.c.prod_id == self._database_class.id,
            )
            .group_by(aggregation_map[aggregated_by])
            .order_by(desc("sustainability_score"))
            .all(),
            columns=[
                f"{aggregated_by}",
                "sustainability_score",
                "ecological_score",
                "social_score",
            ],
        )


def get_cred_by_category(self: GreenDB, credibility_threshold: int = 50) -> pd.DataFrame:
    """
    Function counts products by its sustainability labels credibility, >= 50 is credible,
        < 50 is not credible.

    Args:
        credibility_threshold (int): `credibility_threshold` to evaluate if sustainability
        label is credible or not. Default set as 50.

    Returns:
       pd.DataFrame: Query results as `pd.Dataframe`.
    """
    with self._session_factory() as db_session:

        labels = self.get_sustainability_labels_subquery()

        all_unique = self.get_all_unique_products()

        unique_credible_products = (
            db_session.query(
                all_unique.c.category,
                func.count(all_unique.c.prod_id),
                literal_column("'credible'"),
            )
            .filter(
                all_unique.c.sustainability_label.in_(
                    db_session.query(labels.c.id)
                    .filter(labels.c.cred_credibility >= credibility_threshold)
                    .all()
                )
            )
            .group_by(all_unique.c.category)
            .all()
        )

        unique_not_credible_products = (
            db_session.query(
                all_unique.c.category,
                func.count(all_unique.c.prod_id),
                literal_column("'not_credible'"),
            )
            .filter(
                all_unique.c.sustainability_label.not_in(
                    db_session.query(labels.c.id)
                    .filter(labels.c.cred_credibility >= credibility_threshold)
                    .all()
                )
            )
            .group_by(all_unique.c.category)
            .all()
        )

    return pd.DataFrame(
        unique_credible_products + unique_not_credible_products,
        columns=["category", "product_count", "type"],
    )


def build_default_content(use_cached: bool = True) -> Dict[str, str]:
    if use_cached:
        return {
            "excerpt": '<div class="excerpt"><div class="table-wrapper"><div class="table"><div class="hidden"><a href="https://www.otto.de/p/bettwaesche-flamand-damai-luxurioeses-design-1670814521/#variationId=1670814522" class="table-row product-link"><div class="optional table-cell">Bettwäsche »Flamand«, damai, luxuriöses Design</div><div class="table-cell">LINEN</div><div class="optional table-cell">damai</div><div class="table-cell"><div style="color:#fefefe;background:#47363e" onclick="focusLabel(event, \'certificate:MADE_IN_GREEN_OEKO_TEX\')" class="label">MADE_IN_GREEN_OEKO_TEX</div></div><div class="optional table-cell">79.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/mammut-funktionshose-wanderhose-runbold-zip-off-CS0A150Y7/#variationId=S0A150Y79Q7H" class="table-row product-link"><div class="optional table-cell">Mammut Outdoorhose »Runbold Zip Off Pants Women«</div><div class="table-cell">PANTS</div><div class="optional table-cell">Mammut</div><div class="table-cell"><div style="color:#fefefe;background:#402ca0" onclick="focusLabel(event, \'certificate:BLUESIGN_PRODUCT\')" class="label">BLUESIGN_PRODUCT</div></div><div class="optional table-cell">79.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/gq65ls01tau-qled-fernseher-S034K0V9/#variationId=S034K0V92GJ1" class="table-row product-link"><div class="optional table-cell">- GQ65LS01TAU QLED-Fernseher</div><div class="table-cell">TV</div><div class="optional table-cell">-</div><div class="table-cell"><div style="color:#fefefe;background:#5b4825" onclick="focusLabel(event, \'certificate:EU_ENERGY_LABEL_G\')" class="label">EU_ENERGY_LABEL_G</div></div><div class="optional table-cell">1399.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/bosch-waschmaschine-wuu28t48-8-kg-1400-u-min-1693262958/#variationId=1693264134" class="table-row product-link"><div class="optional table-cell">BOSCH Waschmaschine WUU28T48, 8 kg, 1400 U/min</div><div class="table-cell">WASHER</div><div class="optional table-cell">BOSCH</div><div class="table-cell"><div style="color:#fefefe;background:#a64951" onclick="focusLabel(event, \'certificate:EU_ENERGY_LABEL_A\')" class="label">EU_ENERGY_LABEL_A</div> <div style="color:#bbbbbb;background:#3f3f3f" onclick="focusLabel(event, \'certificate:OTHER\')" class="label">OTHER</div></div><div class="optional table-cell">659.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wunderwerk-chinos-june-chino-S00330DQ/#variationId=S00330DQ3711" class="table-row product-link"><div class="optional table-cell">wunderwerk Chinos »June chino«</div><div class="table-cell">PANTS</div><div class="optional table-cell">wunderwerk</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div> <div style="color:#bbbbbb;background:#3f3f3f" onclick="focusLabel(event, \'certificate:OTHER\')" class="label">OTHER</div></div><div class="optional table-cell">129.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/von-jungfeld-socken-geschenk-box-S0O1E091/#variationId=S0O1E091JSDC" class="table-row product-link"><div class="optional table-cell">von Jungfeld Socken Geschenk Box</div><div class="table-cell">SOCKS</div><div class="optional table-cell">von Jungfeld</div><div class="table-cell"><div style="color:#bbbbbb;background:#3f3f3f" onclick="focusLabel(event, \'certificate:ECOCERT\')" class="label">ECOCERT</div> <div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">28.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-runrunrun-red-1-tlg-S0J5X0AM/#variationId=S0J5X0AM1SWF" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »RunRunRun red« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div> <div style="color:#bbbbbb;background:#3f3f3f" onclick="focusLabel(event, \'certificate:OTHER\')" class="label">OTHER</div></div><div class="optional table-cell">29.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/erlich-textil-boxershorts-schwarz-erc82o002-q11.html" class="table-row product-link"><div class="optional table-cell">KARL - Boxershorts - schwarz</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">Erlich Textil</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">25.46</div><div class="optional table-cell">EUR</div></a><a href="https://www.amazon.co.uk/G-STAR-RAW-T-Shirt-White-C336-110/dp/B09CGWF9SJ/ref=sr_1_40" class="table-row product-link"><div class="optional table-cell">G-STAR RAW Foxy Boxy T-Shirt</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">G-STAR RAW Store</div><div class="table-cell"><div style="color:#fefefe;background:#66362a" onclick="focusLabel(event, \'certificate:GOTS_MADE_WITH_ORGANIC_MATERIALS\')" class="label">GOTS_MADE_WITH_ORGANIC_MATERIALS</div></div><div class="optional table-cell">24.0</div><div class="optional table-cell">GBP</div></a><a href="https://www.otto.de/p/petite-fleur-taillenslip-packung-5-st-455237761/#variationId=461797530" class="table-row product-link"><div class="optional table-cell">petite fleur Taillenslip (Packung, 5-St)</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">petite fleur</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">16.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-disney-classics-womens-lip-embroidery-t-shirt-print-black-h3a21d0zz-q11.html" class="table-row product-link"><div class="optional table-cell">DNCA LIP EMBROIDERY - T-Shirt print - black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">26.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/givn-berlin-aria-strickpullover-dark-pink-gip21i004-j11.html" class="table-row product-link"><div class="optional table-cell">ARIA - Strickpullover - dark pink</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Givn Berlin</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">99.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/watapparel-t-shirt-print-dark-heather-grey-w0o22o04a-q11.html" class="table-row product-link"><div class="optional table-cell">MOUNTAINS - T-Shirt print - dark heather grey</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">watapparel</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">19.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/h-i-s-poloshirt-in-markanter-melange-optik-1014332360/#variationId=1379257094" class="table-row product-link"><div class="optional table-cell">H.I.S Poloshirt in markanter Melange Optik</div><div class="table-cell">SHIRT</div><div class="optional table-cell">H.I.S</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">14.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/ulla-popken-gilet-gris-sable-up121i0l7-o11.html" class="table-row product-link"><div class="optional table-cell">Gilet - gris sable</div><div class="table-cell">JACKET</div><div class="optional table-cell">Ulla Popken</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/lady-schlupfbluse-1685019948/#variationId=1685019999" class="table-row product-link"><div class="optional table-cell">Lady Schlupfbluse</div><div class="table-cell">BLOUSE</div><div class="optional table-cell">Lady</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/organication-sweatjacke-coffee-brown-orw21j01p-o11.html" class="table-row product-link"><div class="optional table-cell">JALE OVERSIZE FULL  - Sweatjacke - coffee brown</div><div class="table-cell">JACKET</div><div class="optional table-cell">ORGANICATION</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">69.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/repeat-cardigan-black-r0021i06u-q11.html" class="table-row product-link"><div class="optional table-cell">CARDIGAN - Cardigan - black</div><div class="table-cell">JACKET</div><div class="optional table-cell">Repeat</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">219.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.de/marc-opolo-denim-freizeitkleid-white-blush-op521c07p-a11.html" class="table-row product-link"><div class="optional table-cell">Maxikleid - white blush</div><div class="table-cell">DRESS</div><div class="optional table-cell">Marc O\'Polo DENIM</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">59.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/grobund-svala-faltenrock-dark-blue-grw21b00b-k12.html" class="table-row product-link"><div class="optional table-cell">SVALA - A-Linien-Rock - dark blue</div><div class="table-cell">SKIRT</div><div class="optional table-cell">GROBUND</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">119.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/camano-6-pack-socken-black-c5181000q-q11.html" class="table-row product-link"><div class="optional table-cell">6 PACK - Socken - black</div><div class="table-cell">SOCKS</div><div class="optional table-cell">camano</div><div class="table-cell"><div style="color:#fefefe;background:#66362a" onclick="focusLabel(event, \'certificate:GOTS_MADE_WITH_ORGANIC_MATERIALS\')" class="label">GOTS_MADE_WITH_ORGANIC_MATERIALS</div></div><div class="optional table-cell">15.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/snocks-chaussettes-schwarz-sne810006-q11.html" class="table-row product-link"><div class="optional table-cell">6 PACK - Chaussettes - schwarz</div><div class="table-cell">SOCKS</div><div class="optional table-cell">SNOCKS</div><div class="table-cell"><div style="color:#fefefe;background:#66362a" onclick="focusLabel(event, \'certificate:GOTS_MADE_WITH_ORGANIC_MATERIALS\')" class="label">GOTS_MADE_WITH_ORGANIC_MATERIALS</div></div><div class="optional table-cell">29.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/melawear-top-weiss-mex21e006-a11.html" class="table-row product-link"><div class="optional table-cell">PINA - Top - weiß</div><div class="table-cell">TOP</div><div class="optional table-cell">MELA</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">24.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/arizona-pyjama-2-tlg-1-stueck-mit-karo-muster-1535456612/#variationId=1535456811" class="table-row product-link"><div class="optional table-cell">Arizona Pyjama (2 tlg., 1 Stück) mit Karo Muster</div><div class="table-cell">NIGHTWEAR</div><div class="optional table-cell">Arizona</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-basics-langarmshirt-shirt-1-tlg-938856150/#variationId=1197381083" class="table-row product-link"><div class="optional table-cell">Classic Basics Langarmshirt »Shirt« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Classic Basics</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">13.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/inspirationen-7-8-jeans-1-tlg-1533464934/#variationId=1533477570" class="table-row product-link"><div class="optional table-cell">Inspirationen 7/8-Jeans (1-tlg)</div><div class="table-cell">JEANS</div><div class="optional table-cell">Inspirationen</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">34.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/casual-looks-bequeme-jeans-1-tlg-1670209068/#variationId=1670218376" class="table-row product-link"><div class="optional table-cell">Casual Looks Bequeme Jeans (1-tlg)</div><div class="table-cell">PANTS</div><div class="optional table-cell">Casual Looks</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">49.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/the-organic-company-sac-a-main-clay-t6x54h002-c12.html" class="table-row product-link"><div class="optional table-cell">STORAGE - Sac de sport - clay</div><div class="table-cell">BAG</div><div class="optional table-cell">The Organic Company</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">34.99</div><div class="optional table-cell">EUR</div></a></div><div class="table-row"><div class="optional table-header">name</div><div class="table-header">category</div><div class="optional table-header">brand</div><div class="table-header">labels</div><div class="optional table-header">price</div><div class="optional table-header">currency</div></div><a href="https://www.otto.de/p/venice-beach-t-shirt-packung-2-tlg-868865409/#variationId=868866676" class="table-row product-link"><div class="optional table-cell">Venice Beach T-Shirt (Packung, 2-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Venice Beach</div><div class="table-cell"><div style="color:#fefefe;background:#324e2a" onclick="focusLabel(event, \'certificate:COTTON_MADE_IN_AFRICA\')" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">21.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/tezenis-top-bianco-teg21e014-a11.html" class="table-row product-link"><div class="optional table-cell">breiten und  - Top - bianco</div><div class="table-cell">TOP</div><div class="optional table-cell">Tezenis</div><div class="table-cell"><div style="color:#fefefe;background:#66362a" onclick="focusLabel(event, \'certificate:GOTS_MADE_WITH_ORGANIC_MATERIALS\')" class="label">GOTS_MADE_WITH_ORGANIC_MATERIALS</div></div><div class="optional table-cell">8.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/cellbes-t-shirt-basic-greenblack-ckg21d002-m11.html" class="table-row product-link"><div class="optional table-cell">2 PACK - T-Shirt basic - green/black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Cellbes</div><div class="table-cell"><div style="color:#fefefe;background:#682464" onclick="focusLabel(event, \'certificate:GOTS_ORGANIC\')" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">39.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/vaude-rucksack-tecolog-ii-14-city-C1565288947/#variationId=1565303563" class="table-row product-link"><div class="optional table-cell">VAUDE Cityrucksack »TECOLOG«</div><div class="table-cell">BACKPACK</div><div class="optional table-cell">VAUDE</div><div class="table-cell"><div style="color:#fefefe;background:#318f36" onclick="focusLabel(event, \'certificate:GREEN_BUTTON\')" class="label">GREEN_BUTTON</div></div><div class="optional table-cell">48.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/ethletic-fair-sneaker-low-black-etd15o01q-q11.html" class="table-row product-link"><div class="optional table-cell">FAIR - Sneaker low - black</div><div class="table-cell">SNEAKERS</div><div class="optional table-cell">Ethletic</div><div class="table-cell"><div style="color:#fefefe;background:#b75439" onclick="focusLabel(event, \'certificate:FAIRTRADE_COTTON\')" class="label">FAIRTRADE_COTTON</div></div><div class="optional table-cell">109.9</div><div class="optional table-cell">EUR</div></a></div></div><button class="btn" onclick="\n    event.target.disabled = true;\n    setTimeout(function() {{\n        const stuff = event.target.parentNode.getElementsByClassName(&quot;hidden&quot;)[0];\n        const table = stuff.parentNode;\n        for(var i = 0; i &lt; 4 &amp;&amp; stuff.childNodes.length &gt; 0; i++) {{\n            const k = Math.floor(Math.random() * stuff.childNodes.length);\n            table.appendChild(stuff.childNodes[k]);\n        }}\n        event.target.disabled = stuff.childNodes.length == 0;\n    }}, 400);\n    ">more</button></div>',  # noqa
            "plot_category_cred": '<div>                            <div id="e307be3e-2aaf-49bf-a47c-f75563294f3a" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("e307be3e-2aaf-49bf-a47c-f75563294f3a")) {                    Plotly.newPlot(                        "e307be3e-2aaf-49bf-a47c-f75563294f3a",                        [{"name":"not credible","x":["OVEN","TABLET","COOKER_HOOD","STOVE","SMARTWATCH","HEADSET","HEADPHONES","SWIMWEAR","BAG","DRYER","SNEAKERS","SHOES","SMARTPHONE","LAPTOP","TRACKSUIT","SOCKS","BACKPACK","OVERALL","DRESS","SUIT","SKIRT","JACKET","SHORTS","BLOUSE","SWEATER","TOWEL","JEANS","UNDERWEAR","TOP","SHIRT","PANTS","TSHIRT","FRIDGE","NIGHTWEAR","DISHWASHER","WASHER","FREEZER","PRINTER","LINEN","TV"],"y":[443,1275,406,263,349,60,7395,16973,37328,239,11026,97487,2172,5721,1825,22957,4582,2821,40767,2110,8727,62648,3859,22236,73634,4858,17888,52195,15179,96414,55958,32675,196,8673,192,509,50,280,443,36],"type":"bar"},{"name":"credible","x":["OVEN","TABLET","COOKER_HOOD","STOVE","SMARTWATCH","HEADSET","HEADPHONES","SWIMWEAR","BAG","DRYER","SNEAKERS","SHOES","SMARTPHONE","LAPTOP","TRACKSUIT","SOCKS","BACKPACK","OVERALL","DRESS","SUIT","SKIRT","JACKET","SHORTS","BLOUSE","SWEATER","TOWEL","JEANS","UNDERWEAR","TOP","SHIRT","PANTS","TSHIRT","FRIDGE","NIGHTWEAR","DISHWASHER","WASHER","FREEZER","PRINTER","LINEN","TV"],"y":[0,0,0,0,0,0,0,104,440,3,139,1438,36,117,48,1583,330,244,5283,328,1362,11320,707,4665,17223,1217,5046,14826,4545,30647,23495,16618,158,7048,187,558,88,770,2522,831],"type":"bar"}],                        {"barmode":"stack","barnorm":"fraction","title":{"text":"Normalized product count with vs. without credibility by category."},"yaxis":{"title":{"text":"credibility"}},"template":{"data":{"histogram2dcontour":[{"type":"histogram2dcontour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"choropleth":[{"type":"choropleth","colorbar":{"outlinewidth":0,"ticks":""}}],"histogram2d":[{"type":"histogram2d","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmap":[{"type":"heatmap","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmapgl":[{"type":"heatmapgl","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"contourcarpet":[{"type":"contourcarpet","colorbar":{"outlinewidth":0,"ticks":""}}],"contour":[{"type":"contour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"surface":[{"type":"surface","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"mesh3d":[{"type":"mesh3d","colorbar":{"outlinewidth":0,"ticks":""}}],"scatter":[{"fillpattern":{"fillmode":"overlay","size":10,"solidity":0.2},"type":"scatter"}],"parcoords":[{"type":"parcoords","line":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolargl":[{"type":"scatterpolargl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"scattergeo":[{"type":"scattergeo","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolar":[{"type":"scatterpolar","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"scattergl":[{"type":"scattergl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatter3d":[{"type":"scatter3d","line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattermapbox":[{"type":"scattermapbox","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterternary":[{"type":"scatterternary","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattercarpet":[{"type":"scattercarpet","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"pie":[{"automargin":true,"type":"pie"}]},"layout":{"autotypenumbers":"strict","colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"hovermode":"closest","hoverlabel":{"align":"left"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"bgcolor":"#E5ECF6","angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"ternary":{"bgcolor":"#E5ECF6","aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]]},"xaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"yaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"geo":{"bgcolor":"white","landcolor":"#E5ECF6","subunitcolor":"white","showland":true,"showlakes":true,"lakecolor":"white"},"title":{"x":0.05},"mapbox":{"style":"light"}}}},                        {"staticPlot": true, "responsive": true}                    )                };                            </script>        </div>',  # noqa
            "stats": '<table>\n<thead>\n<tr>\n<th style="text-align:right"></th>\n<th style="text-align:left"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align:right"><strong>2023-02-10</strong></td>\n<td style="text-align:left">last updated</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>10,963,919</strong></td>\n<td style="text-align:left">pages scraped</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>866,882</strong></td>\n<td style="text-align:left">unique products</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>153,701</strong></td>\n<td style="text-align:left">unique products with credible sustainability labels</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>41</strong></td>\n<td style="text-align:left">product categories</td>\n</tr>\n</tbody>\n</table>\n',  # noqa
        }

    db = GreenDB()
    scraping = {name: Scraping(name) for name in ALL_SCRAPING_TABLE_NAMES}

    total_scrapes = sum(
        table.get_scraped_page_count_per_merchant_and_country()["scraped_page_count"].sum()
        for table in scraping.values()
    )
    all_categories = [category.value for category in ProductCategory]
    products_per_cred = plots.fetch_product_count_by_sustainability_label_credibility(db)
    products_per_country = plots.fetch_latest_product_count_per_merchant_and_country(db)

    stats = render_markdown(
        "| | |\n"
        "| -: | :- |\n"
        f"| **{products_per_country['latest_extraction_timestamp']}** | last updated |\n"
        f"| **{total_scrapes:,}** | pages scraped |\n"
        f"| **{products_per_cred['all_unique_product_count']:,}** | unique products |\n"
        f"| **{products_per_cred['unique_credible_product_count']:,}** | unique products with credible sustainability labels |\n"  # noqa
        f"| **{len(all_categories)}** | product categories |\n"
    )

    category_cred = get_cred_by_category(db)
    category_cred["category"] = category_cred["category"].apply(lambda x: category_typos.get(x, x))
    category_cred_ratio = category_cred.pivot_table(
        "product_count", "category", "type", fill_value=0, aggfunc="sum"
    )
    category_cred_ratio["ratio"] = category_cred_ratio["credible"] / (
        category_cred_ratio["credible"] + category_cred_ratio["not_credible"]
    )
    category_cred_ratio = category_cred_ratio.sort_values("ratio")

    plot_category_cred = go.Figure(
        data=[
            go.Bar(
                name="not credible",
                x=category_cred_ratio.index,
                y=category_cred_ratio["not_credible"],
            ),
            go.Bar(
                name="credible",
                x=category_cred_ratio.index,
                y=category_cred_ratio["credible"],
            ),
        ],
        layout=go.Layout(
            title="Normalized product count with vs. without credibility by category.",
            yaxis_title="credibility",
            barmode="stack",
            barnorm="fraction",
        ),
    )

    return dict(
        excerpt=render_excerpt(filter_products(get_relevant_products(db, 500), 33)),
        plot_category_cred=render_plotly_figure(plot_category_cred),
        stats=stats,
    )


def render_label_data() -> str:
    left = 'style="text-align:left"'
    right = 'style="text-align:right"'
    return f"""
<table>
<thead><tr><th {left}>metric</th><th {right}>rating</th></tr></thead>
</table>

<div class="label_metrics label_cred">
<table>
<tbody>
<tr><td {left}>Credibility</td><td id="label_cred_credibility" {right}></td></tr>
</tbody>
</table>
</div>

<div class="label_metrics label_eco">
<table>
<tbody>
<tr>
<td {left}>Chemical use</td>
<td id="label_eco_chemicals" {right}></td>
</tr>
<tr>
<td {left}>Product lifetime</td>
<td id="label_eco_lifetime" {right}></td>
</tr>
<tr>
<td {left}>Water use</td>
<td id="label_eco_water" {right}></td>
</tr>
<tr>
<td {left}>Inputs</td>
<td id="label_eco_inputs" {right}></td>
</tr>
<tr>
<td {left}>Product quality</td>
<td id="label_eco_quality" {right}></td>
</tr>
<tr>
<td {left}>Energy use</td>
<td id="label_eco_energy" {right}></td>
</tr>
<tr>
<td {left}>Waste and air polution</td>
<td id="label_eco_waste_air" {right}></td>
</tr>
<tr>
<td {left}>Environmental management</td>
<td id="label_eco_environmental_management" {right}></td>
</tr>
</tbody>
</table>
</div>

<div class="label_metrics label_social">
<table>
<tbody>
<tr>
<td {left}>Labour rights and working conditions</td>
<td id="label_social_labour_rights" {right}></td>
</tr>
<tr>
<td {left}>Ethical business practice</td>
<td id="label_social_business_practice" {right}></td>
</tr>
<tr>
<td {left}>Social rights</td>
<td id="label_social_social_rights" {right}></td>
</tr>
<tr>
<td {left}>Company responsibility</td>
<td id="label_social_company_responsibility" {right}></td>
</tr>
<tr>
<td {left}>Conflict minerals</td>
<td id="label_social_conflict_minerals" {right}></td>
</tr>
</tbody>
</table>
</div>
"""


def rebuild_landing_page(
    content_map: Dict[str, str] = {},
    use_cached_content: bool = True,
    page_title: str = "GreenDB",
    description: str = "A Product-by-Product Sustainability Database",
    page_url: str = "https://calgo-lab.github.io/greendb",
    image_url: str = "https://calgo-lab.github.io/greendb/greendb.jpg",
    image_alt_text: str = "GreenDB",
    regenerate_color_scheme: bool = False,
) -> str:
    """builds the"""

    content = build_default_content(use_cached_content) | content_map
    print(content)
    content["label_name"] = '<h1 id="label_name"></h1>'
    content["label_description"] = '<p id="label_description"></p>'
    content["label_data"] = render_label_data()

    class Content(Element):
        name: str

        def open(self) -> Any:
            return self.close()

        def render(self, **kwargs: Any) -> str:
            assert self.name in content, f"content not found '{self.name}'"
            return content[self.name]

    width_classes: Dict[float, str] = {}

    def width_class(width: float) -> str:
        if width not in width_classes:
            width_classes[width] = f"col{len(width_classes)}"
        return width_classes[width]

    class Column(Element):
        row = None
        weight: int = 1

        def add_column(self, column: Any) -> list:
            if self.row is None:
                self.row = [self]
            self.row.append(column)
            return self.row

        def on_add_to_parent(self, parent: Any) -> None:
            if self.weight > 0 and parent.children and isinstance(parent.children[-1], Column):
                self.row = parent.children[-1].add_column(self)

        def on_close_parent(self) -> Any:
            self.html_tag = "div"
            self.css_class.append("ff")
            self.css_class.append("col")
            if self.row is not None:
                total_weight = sum(col.weight for col in self.row)
                self.css_class.append(width_class(self.weight / total_weight))

    element_map = {"column": Column, "content": Content}
    with open("landing-page.md", "r", encoding="utf-8") as file:
        body = render_page(file.read(), element_map)

    if regenerate_color_scheme:
        tint = [medium(random(), 8) for i in range(3)]
        tint_hover = [blend(a, random(), 0.1) for a in tint]
        link = [0.3, 0.3, 1]
        link_hover = [blend(medium(random(), 5), a, 0.25) for a in link]
        excerpt = [medium(random(), 12) for i in range(3)]
        excerpt_hover = [blend(a, medium(random(), 2), 0.2) for a in excerpt]
        more = [blend(a, blend(medium(random(), 80), b, 0.2), 0.4) for a, b in zip(excerpt, tint)]
        more_hover = [blend(a, medium(random(), 20), 0.1) for a in more]
        print("tint =", tint)
        print("tint_hover =", tint_hover)
        print("link =", link)
        print("link_hover =", link_hover)
        print("excerpt =", excerpt)
        print("excerpt_hover =", excerpt_hover)
        print("more =", more)
        print("more_hover =", more_hover)
    else:
        tint = [0.8875641033692422, 0.11477726792017197, 0.16015838304306768]
        tint_hover = [0.7123934468023223, 0.1067043569269721, 0.16688851531012477]
        link = [0.3, 0.3, 1]
        link_hover = [0.19027607418965353, 0.32350485353551683, 0.7116513755412007]
        excerpt = [0.13704307356519763, 0.15924943484172588, 0.5812938149278745]
        excerpt_hover = [0.14373655108035288, 0.12412299681563652, 0.39106001494835]
        more = [0.1485823416814057, 0.23921176685507542, 0.9116386929265479]
        more_hover = [0.15729714510147194, 0.22121801304040017, 0.783397636799458]

    foot = [blend(a, 0.005, 0.92) for a in tint_hover]
    white = [1, 1, 1]
    dark = [0.01, 0.01, 0.015]

    return minify(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<style>

.row::before,
.row::after {{
    display: table;
    content: "";
}}

.row::after {{
    clear: both;
}}

.ff {{
    padding: 0 25px;
}}

.container {{
    margin-right: auto;
    margin-left: auto;
}}

.overlay {{
    overflow-y: auto;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: #0008
    z-index: 2;
    cursor: pointer;
    display: none;
    padding: 25px 0;
}}

.overlay .container {{
    padding: 25px;
    border-radius: 15px;
    background: white;
}}

.label_metrics {{
    color: white;
    margin: 20px 0;
    border-radius: 6.5px;
    padding: 4px;
}}
.label_cred {{
    background: {webcolor(label_cred_tint)};
}}

.label_eco {{
    background: {webcolor(label_eco_tint)};
}}

.label_social {{
    background: {webcolor(label_social_tint)};
}}

@media (prefers-color-scheme: dark) {{
    body {{
        color: white;
        background: #131315;
    }}
    .container {{
        padding: 25px;
        background: {webcolor(dark)};
    }}
    .overlay .container {{
        background: {webcolor(dark)};
    }}
    .btn {{ box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, dark, tint))} }}
    .btn:hover {{ box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, dark, tint_hover))} }}
    .btn:active {{ box-shadow: inset 0px 5px 5px 0px {webcolor(map(shadow, tint, dark))} }}
    .excerpt .btn {{ box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, dark, more))} }}
    .excerpt .btn:hover {{ box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, dark, more_hover))} }}
    .excerpt .btn:active {{ box-shadow: inset 0px 5px 5px 0px {webcolor(map(shadow, more, dark))} }}
    .excerpt .btn:disabled {{ box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, dark, more))} }}
    .link {{
        color: {webcolor(link)}
    }}
    .link:hover {{
        color: {webcolor(link_hover)}
    }}
    footer {{
        background: none;
    }}
}}

/*
@media (max-width:768px) {{
    .optional {{ display:none }}
}}
*/

@media (min-width:768px) {{
    .container {{ width:750px }}
}}

@media (min-width:992px) {{
    .container {{ width:970px }}
    .col {{ float: left }}
    {''.join(f'.{name} {{ width: {width*100}% }}'
        for width, name in width_classes.items())}
}}

@media (min-width:1200px) {{
    .container {{ width:1170px }}
}}

.stats {{
    font-size: 1.1em;
}}

.stats td:first-child {{
    white-space: nowrap;
}}

* {{
    box-sizing: border-box;
    animation-timing-function: cubic-bezier(.19,1,.22,1);
}}

@keyframes disappear {{
    0% {{opacity:1}}
    to {{opacity:0}}
}}

@keyframes appear {{
    0% {{opacity:0}}
    to {{opacity:1}}
}}

body {{
    font-family: 'Muli', 'Helvetica', 'Arial', 'sans-serif';
    line-height: 1.42;
    font-size: 14px;
    margin:0;
}}

a {{
    text-decoration: none;
}}

p {{
    font-size: 1.2em;
    line-height: 2rem;
}}

li {{
    font-size: 1.1em;
    line-height: 1.7rem;
}}

h1 {{
    font-size: 2.25em;
}}

section {{
    padding: 20px 0;
}}

.container {{
    padding: 10px;
}}

footer {{
    padding: 40px 0px;
    text-align: center;
    background: {webcolor(foot)};
    color: white;
}}

.excerpt .hidden {{
    display: none;
}}

.table-wrapper {{
    overflow-x: auto;
    margin-bottom: 20px;
}}

.excerpt {{
    text-align: center;
}}

.excerpt div {{
    text-align: left;
}}

.excerpt .btn {{
    width: 100%;
    padding: 8px;
    font-size: 1em;
    outline: 0;
    margin: 0;
    border-radius: 6.5px;
    background: {webcolor(more)};
    box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, white, more))};
    animation-name: appear;
    animation-duration: 1.5s;
}}

.excerpt .btn:hover {{
    background: {webcolor(more_hover)};
    box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, white, more_hover))};
}}

.excerpt .btn:active {{
    background: {webcolor(more)};
    box-shadow: inset 0px 5px 5px 0px {webcolor(map(shadow, more, white))};
}}

.excerpt .btn:disabled {{
    cursor: default;
    background: {webcolor(more)};
    box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, white, more))};
    animation-name: disappear;
    animation-duration: .3s;
    opacity: 0;
}}

.product-link .table-cell {{
    padding: 12px;
}}

.product-link {{
    color: white;
    background: {webcolor(excerpt)};
    -ms-touch-action: manipulation;
    touch-action: manipulation;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    background-image: none;
    user-select: none;
    animation-name: appear;
    animation-duration: 1s;
}}

.product-link:nth-child(even) {{
    background: {webcolor(excerpt_hover)};
    box-shadow: inset 0px 2px 3px 0px {webcolor(map(shadow, excerpt_hover, excerpt))};
}}

.product-link .label {{
    padding: 8px;
    margin: 2px;
    display: inline;
    border-radius: 3.5px;
}}

{''.join(f'''
.product-link .{label} {{
    color: {webcolor(color)};
    background: {webcolor(idle)};
    box-shadow: 0px 3px 3px 0px {webcolor(map(shadow, excerpt, idle))},
        inset 0 0 2px 0 {webcolor(map(bevel, excerpt, idle, [medium(t, 2) for t in idle]))};
}}

.product-link:nth-child(even) .{label} {{
    box-shadow: 0px 3px 3px 0px {webcolor(map(shadow, excerpt_hover, idle))},
        inset 0 0 2px 0 {webcolor(map(bevel, excerpt_hover, idle, [medium(t, 2) for t in idle]))};
}}

.product-link .{label}:hover {{
    background: {webcolor(hover)};
    box-shadow: 0px 3px 3px 0px {webcolor(map(shadow, excerpt, hover))},
        inset 0 0 2px 0 {webcolor(map(bevel, excerpt, hover, [medium(t, 2) for t in hover]))};
}}

.product-link:nth-child(even) .{label}:hover {{
    box-shadow: 0px 3px 3px 0px {webcolor(map(shadow, excerpt_hover, hover))},
        inset 0 0 2px 0 {webcolor(map(bevel, excerpt_hover, hover, [medium(t, 2) for t in hover]))};
}}

.product-link .{label}:active {{
    background: {webcolor(idle)};
    box-shadow: inset 0px 3px 3px 0px {webcolor(map(shadow, idle, excerpt))};
}}

.product-link:nth-child(even) .{label}:active {{
    box-shadow: inset 0px 3px 3px 0px {webcolor(map(shadow, idle, excerpt_hover))};
}}
'''
    for label, (color, idle, hover) in label_colors.items()
)}

.btn {{
    margin: 7px;
    border: none;
    border-radius: 4.3px;
    padding: 15px;
    font-size: 1.15em;
    font-weight: 400;
    font-family: sans-serif;
    vertical-align: middle;
    text-align: center;
    letter-spacing: 2px;
    display: inline-block;
    color: white;
    background: {webcolor(tint)};
    box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, white, tint))};
    -ms-touch-action: manipulation;
    touch-action: manipulation;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    background-image: none;
    user-select: none;
}}

.btn:hover {{
    background: {webcolor(tint_hover)};
    box-shadow: 0px 5px 5px 0px {webcolor(map(shadow, white, tint_hover))};
}}

.btn:active {{
    background: {webcolor(tint)};
    box-shadow: inset 0px 5px 5px 0px {webcolor(map(shadow, tint, white))};
}}

.table {{ display: table }}
.table-row {{ display: table-row }}
.table-cell {{ display: table-cell }}
.table-header {{ display: table-cell }}

.table,
table {{
    width: 100%;
    max-width: 100%;
    line-height: 1.2;
    background-color: transparent;
    border-spacing: 0;
    border-collapse: collapse;
}}

.table-header,
th {{ font-size: 1.1em; }}

.table-header,
.table-cell,
th,
td {{ padding: 8px; }}

</style>
<script type="text/javascript">
window.PlotlyConfig={{MathJaxConfig:'local'}};
{get_plotlyjs()}
</script>
<meta name="description" content="{description}">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:alt" content="{image_alt_text}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:url" content="{page_url}">
<link rel="canonical" href="{page_url}">
<link rel="icon" href="/favicon.ico">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link href="https://fonts.googleapis.com/css?family=Lato:400,600" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Muli:400,600" rel="stylesheet">
</head>
{body}
<script>

const label_overlay = document.getElementById("label_overlay");
const label_name = document.getElementById("label_name");
const label_description = document.getElementById("label_description");
{"".join(f'const {id} = document.getElementById("{id}");' for id,name in label_metrics)}
const label_info = {js_label_info};

label_overlay.addEventListener("click", function(event) {{
    label_overlay.style.display = "none";
    document.body.style.overflow = "";
}})

function focusLabel(event, label) {{
    event.stopPropagation();
    event.preventDefault();
    label_overlay.style.display = "block";
    document.body.style.overflow = "hidden";
    const info = label_info[label];
    label_name.innerText = info.name;
    label_description.innerText = info.description;
    {"".join(f'{id}.innerText = info.{name}+"%";' for id,name in label_metrics)}
}}

</script>
</html>""",
        minify_js=True,
        minify_css=True,
    )


if __name__ == "__main__":
    content = rebuild_landing_page()
    with open("../../index.html", "w", encoding="utf-8") as f:
        f.write(content)
