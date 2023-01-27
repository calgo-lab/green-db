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
    return "#" + "".join(f"{int(to_srgb(c)*255):02x}" for c in color)


def linspace(start: float, end: float, n: int) -> List[float]:
    return [start + (end - start) * i / (n - 1) for i in range(n)]


def animate(curve: list) -> List[Tuple[int, Any]]:
    return [(i * 100 // (len(curve) - 1), c) for i, c in enumerate(curve)]


def render_plotly_figure(
    fig: Any, width: Any = "100%", height: Any = "100%", div_id: Optional[str] = None
) -> str:
    return to_html(
        fig,
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


def render_label(label: str) -> str:
    label_info = label_map[label]
    cred = label_info.cred_credibility or 0
    seed(label + "1")
    tint = [kurgel(random() * 6, random()) for i in range(3)]
    color = [blend(t, 0.05, 1 - cred / 100) for t in tint]
    return render_tag(
        "div",
        None,
        ["label"],
        re.sub(r"^certificate:", "", label),
        [f'style="background:{webcolor(color)}"'],
    )


def product2dict(product: Product) -> dict:
    category_hack = {"PANT": "PANTS", "SHORT": "SHORTS", "JEAN": "JEANS", "SWIMMWEAR": "SWIMWEAR"}
    replacements = dict(
        labels=" ".join(render_label(label) for label in product.sustainability_labels),
        category=category_hack.get(product.category, product.category),
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


def get_relevant_products(
    self: GreenDB, count: int, credibility_threshold: int = 50
) -> List[Product]:
    """
    Fetch `count` products at random.

    Yields:
        Iterator[Product]: `Iterator` of domain object representation
    """
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
            .filter(
                or_(
                    *[
                        self._database_class.sustainability_labels.any(label)
                        for label in credible_labels
                    ]
                )
            )
            .filter(func.length(self._database_class.name) < 60)
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
            "plot_category_cred": '<div>                            <div id="5bfd4de7-6b93-487d-8041-17907a8d1b81" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("5bfd4de7-6b93-487d-8041-17907a8d1b81")) {                    Plotly.newPlot(                        "5bfd4de7-6b93-487d-8041-17907a8d1b81",                        [{"name":"not credible","x":["OVEN","STOVE","SMARTWATCH","COOKER_HOOD","TABLET","HEADSET","HEADPHONES","SWIMMWEAR","SWIMWEAR","BAG","SNEAKERS","SMARTPHONE","SHOES","LAPTOP","TRACKSUIT","DRYER","SOCKS","BACKPACK","OVERALL","DRESS","SKIRT","SUIT","JACKET","SHORTS","BLOUSE","TOWEL","JEANS","SWEATER","SHIRT","TOP","UNDERWEAR","PANT","TSHIRT","PANTS","WASHER","FRIDGE","NIGHTWEAR","DISHWASHER","FREEZER","PRINTER","LINEN","TV"],"y":[425,239,264,396,1042,48,5315,10910,5679,36103,9173,1629,74451,4012,1942,227,21158,3979,2729,38999,8379,1891,58467,3403,21399,4447,17050,58863,96311,14268,42133,33436,29514,19842,490,201,7913,186,48,276,414,34],"type":"bar"},{"name":"credible","x":["OVEN","STOVE","SMARTWATCH","COOKER_HOOD","TABLET","HEADSET","HEADPHONES","SWIMMWEAR","SWIMWEAR","BAG","SNEAKERS","SMARTPHONE","SHOES","LAPTOP","TRACKSUIT","DRYER","SOCKS","BACKPACK","OVERALL","DRESS","SKIRT","SUIT","JACKET","SHORTS","BLOUSE","TOWEL","JEANS","SWEATER","SHIRT","TOP","UNDERWEAR","PANT","TSHIRT","PANTS","WASHER","FRIDGE","NIGHTWEAR","DISHWASHER","FREEZER","PRINTER","LINEN","TV"],"y":[0,0,0,0,0,0,0,54,43,401,113,25,1421,106,53,8,1328,317,219,4887,1236,330,10334,635,4369,1101,4373,15658,28726,4340,13964,12348,13410,9543,327,147,6588,155,73,755,2262,681],"type":"bar"}],                        {"barmode":"stack","barnorm":"fraction","title":{"text":"Normalized product count with vs. without credibility by category."},"yaxis":{"title":{"text":"credibility"}},"template":{"data":{"histogram2dcontour":[{"type":"histogram2dcontour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"choropleth":[{"type":"choropleth","colorbar":{"outlinewidth":0,"ticks":""}}],"histogram2d":[{"type":"histogram2d","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmap":[{"type":"heatmap","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmapgl":[{"type":"heatmapgl","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"contourcarpet":[{"type":"contourcarpet","colorbar":{"outlinewidth":0,"ticks":""}}],"contour":[{"type":"contour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"surface":[{"type":"surface","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"mesh3d":[{"type":"mesh3d","colorbar":{"outlinewidth":0,"ticks":""}}],"scatter":[{"fillpattern":{"fillmode":"overlay","size":10,"solidity":0.2},"type":"scatter"}],"parcoords":[{"type":"parcoords","line":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolargl":[{"type":"scatterpolargl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"scattergeo":[{"type":"scattergeo","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolar":[{"type":"scatterpolar","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"scattergl":[{"type":"scattergl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatter3d":[{"type":"scatter3d","line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattermapbox":[{"type":"scattermapbox","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterternary":[{"type":"scatterternary","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattercarpet":[{"type":"scattercarpet","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"pie":[{"automargin":true,"type":"pie"}]},"layout":{"autotypenumbers":"strict","colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"hovermode":"closest","hoverlabel":{"align":"left"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"bgcolor":"#E5ECF6","angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"ternary":{"bgcolor":"#E5ECF6","aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]]},"xaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"yaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"geo":{"bgcolor":"white","landcolor":"#E5ECF6","subunitcolor":"white","showland":true,"showlakes":true,"lakecolor":"white"},"title":{"x":0.05},"mapbox":{"style":"light"}}}},                        {"responsive": true}                    )                };                            </script>        </div>',  # noqa
            "stats": '<table>\n<thead>\n<tr>\n<th style="text-align:right"></th>\n<th style="text-align:left"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align:right"><strong>2023-01-20</strong></td>\n<td style="text-align:left">last updated</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>9,936,634</strong></td>\n<td style="text-align:left">pages scraped</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>778,045</strong></td>\n<td style="text-align:left">unique products</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>140,374</strong></td>\n<td style="text-align:left">unique products with credible sustainability labels</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>41</strong></td>\n<td style="text-align:left">product categories</td>\n</tr>\n</tbody>\n</table>\n',  # noqa
            "excerpt": '<div class="excerpt"><div class="table-wrapper"><div class="table"><div class="hidden"><a href="https://www.zalando.de/les-petits-basics-cafe-croissant-t-shirt-print-white-l4z210017-a11.html" class="table-row product-link"><div class="optional table-cell">CAFE CROISSANT UNISEX - T-Shirt print - white</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Les Petits Basics</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">54.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/kangaroos-sweatshirt-grosse-groessen-637013037/#variationId=637013683" class="table-row product-link"><div class="optional table-cell">KangaROOS Sweatshirt Große Größen</div><div class="table-cell">SWEATER</div><div class="optional table-cell">KangaROOS</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">42.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/petite-fleur-formpants-packung-2-st-seamless-374564496/#variationId=586942967" class="table-row product-link"><div class="optional table-cell">petite fleur Formpants (Packung, 2-St) Seamless</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">petite fleur</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">29.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/tamaris-sweatkleid-in-trendy-maxilaenge-1374197572/#variationId=1496352829" class="table-row product-link"><div class="optional table-cell">Tamaris Sweatkleid in trendy Maxilänge</div><div class="table-cell">DRESS</div><div class="optional table-cell">Tamaris</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">59.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/marc-o-polo-denim-overall-aus-reiner-baumwolle-1652413485/#variationId=1652413507" class="table-row product-link"><div class="optional table-cell">Marc O\'Polo DENIM Overall »aus reiner Baumwolle«</div><div class="table-cell">OVERALL</div><div class="optional table-cell">Marc O\'Polo DENIM</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">99.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/s-oliver-sweathose-mit-seitlichen-rippeneinsatz-1235603975/#variationId=1235604794" class="table-row product-link"><div class="optional table-cell">s.Oliver Sweathose mit seitlichen Rippeneinsatz</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">s.Oliver</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">34.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/cellbes-langarmshirt-dark-blue-ckg21d00h-k11.html" class="table-row product-link"><div class="optional table-cell">Langarmshirt - dark blue</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Cellbes</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">24.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-stranger-things-welcome-to-hawkins-t-shirt-print-black-h3a21d264-q11.html" class="table-row product-link"><div class="optional table-cell">STRANGER THINGS WELCOME TO HAWKINS - T-Shirt print - black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">28.79</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/melrose-rundhalsshirt-mit-glitzer-details-1637111320/#variationId=1637112343" class="table-row product-link"><div class="optional table-cell">Melrose Rundhalsshirt mit Glitzer-Details</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Melrose</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/tamaris-t-shirt-mit-frontprint-1520014353/#variationId=1520014455" class="table-row product-link"><div class="optional table-cell">Tamaris T-Shirt mit Frontprint</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Tamaris</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">20.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/armedangels-malikaa-t-shirt-print-hibiscus-ar321d0i1-h11.html" class="table-row product-link"><div class="optional table-cell">MALIKAA - T-Shirt print - hibiscus</div><div class="table-cell">SHIRT</div><div class="optional table-cell">ARMEDANGELS</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">39.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/bettwaesche-j-d-87078-janine-mit-reissverschluss-1663429671/#variationId=1663429789" class="table-row product-link"><div class="optional table-cell">Bettwäsche »J. D. 87078«, Janine, mit Reißverschluss</div><div class="table-cell">LINEN</div><div class="optional table-cell">Janine</div><div class="table-cell"><div style="background:#47363e" class="label">MADE_IN_GREEN_OEKO_TEX</div></div><div class="optional table-cell">59.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/flashlights-caprijeans-packung-2er-pack-high-waist-1493742093/#variationId=1493747932" class="table-row product-link"><div class="optional table-cell">Flashlights Caprijeans (Packung, 2er-Pack) High Waist</div><div class="table-cell">PANTS</div><div class="optional table-cell">Flashlights</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">47.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/knowledge-cotton-apparel-ribbing-scarf-scarf-kn254g001-c11.html" class="table-row product-link"><div class="optional table-cell">JUNIPER SCARF UNISEX - Scarf - dark grey</div><div class="table-cell">SOCKS</div><div class="optional table-cell">KnowledgeCotton Apparel</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">44.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.de/henry-tiger-t-shirt-print-white-h3a21d366-a11.html" class="table-row product-link"><div class="optional table-cell">MARVEL BADGE - T-Shirt print - white</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">28.79</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/lyle-and-scott-tipped-polo-shirt-navywhite-ly222p039-k12.html" class="table-row product-link"><div class="optional table-cell">TIPPED - Polo shirt - navy/white</div><div class="table-cell">JACKET</div><div class="optional table-cell">Lyle & Scott</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">49.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.otto.de/p/linea-tesini-by-heine-maxikleid-kleid-1551788169/#variationId=1551788187" class="table-row product-link"><div class="optional table-cell">LINEA TESINI by Heine Maxikleid »Kleid«</div><div class="table-cell">DRESS</div><div class="optional table-cell">LINEA TESINI by Heine</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">79.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/bademantel-feel-good-1524338038/#variationId=1524338061" class="table-row product-link"><div class="optional table-cell">Bademantel, feel good</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">feel good</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">35.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-basics-bequeme-jeans-1-tlg-1268680832/#variationId=1268691196" class="table-row product-link"><div class="optional table-cell">Classic Basics Bequeme Jeans (1-tlg)</div><div class="table-cell">PANTS</div><div class="optional table-cell">Classic Basics</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">20.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/boysens-longpullover-uni-oder-gestreift-998599311/#variationId=1041432449" class="table-row product-link"><div class="optional table-cell">Boysen\'s Longpullover uni oder gestreift</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Boysen\'s</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">48.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-kapuzenpullover-black-h3a2101am-q11.html" class="table-row product-link"><div class="optional table-cell">Kapuzenpullover - black</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">58.49</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/living-crafts-schlafhose-carol-S0A2Q0GZ/#variationId=S0A2Q0GZBRFP" class="table-row product-link"><div class="optional table-cell">LIVING CRAFTS Schlafhose »CAROL«</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">LIVING CRAFTS</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/arizona-dehnbund-jeans-paul-805709943/#variationId=805712228" class="table-row product-link"><div class="optional table-cell">Arizona Dehnbund-Jeans »Paul«</div><div class="table-cell">JEANS</div><div class="optional table-cell">Arizona</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-t-shirt-imprime-white-h3a21d2oq-a11.html" class="table-row product-link"><div class="optional table-cell">ALADDIN JASMINE ADVENTURE - T-shirt imprimé - white</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">31.49</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-t-shirt-print-heather-grey-h3a21d3t8-c11.html" class="table-row product-link"><div class="optional table-cell">WANDAVISION ROMANTIC COUPLE - T-Shirt print - heather grey</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">28.79</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-t-shirt-imprime-black-h3a21d0p8-q11.html" class="table-row product-link"><div class="optional table-cell">WANDAVISION WV POSTER 90S - T-shirt imprimé - black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">29.74</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-marvel-black-widow-pop-t-shirt-print-white-h3a2101rs-t11.html" class="table-row product-link"><div class="optional table-cell">BLACK WIDOW BLACK WIDOW POP UNISEX - T-Shirt print - white</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">28.79</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/aeg-waschmaschine-l8tea80560-913143819-6-kg-1500-u-min-1559529134/#variationId=1559529353" class="table-row product-link"><div class="optional table-cell">AEG Waschmaschine L8TEA80560 913143819, 6 kg, 1500 U/min</div><div class="table-cell">WASHER</div><div class="optional table-cell">AEG</div><div class="table-cell"><div style="background:#571e16" class="label">EU_ENERGY_LABEL_B</div> <div style="background:#3f3f3f" class="label">OTHER</div></div><div class="optional table-cell">999.0</div><div class="optional table-cell">EUR</div></a></div><div class="table-row"><div class="optional table-header">name</div><div class="table-header">category</div><div class="optional table-header">brand</div><div class="table-header">labels</div><div class="optional table-header">price</div><div class="optional table-header">currency</div></div><a href="https://www.zalando.de/marc-opolo-denim-kapuzenpullover-cobblestone-op522s02h-b11.html" class="table-row product-link"><div class="optional table-cell">Sweatshirt - cobblestone</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Marc O\'Polo DENIM</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">44.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/vivance-dreams-playsuit-mit-babylocksaum-1361512799/#variationId=1361512816" class="table-row product-link"><div class="optional table-cell">Vivance Dreams Playsuit mit Babylocksaum</div><div class="table-cell">OVERALL</div><div class="optional table-cell">Vivance Dreams</div><div class="table-cell"><div style="background:#324e2a" class="label">COTTON_MADE_IN_AFRICA</div></div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-sweatshirt-black-h3a2100s9-q11.html" class="table-row product-link"><div class="optional table-cell">Sweat à capuche - black</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">61.19</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/lyle-and-scott-pant-pantalon-de-survetement-jet-black-ly222e015-q11.html" class="table-row product-link"><div class="optional table-cell">PANT - Pantalon de survêtement - jet black</div><div class="table-cell">PANTS</div><div class="optional table-cell">Lyle & Scott</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">69.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/armedangels-chemisier-white-ar321e07d-a11.html" class="table-row product-link"><div class="optional table-cell">DAAPHNA - Chemisier - white</div><div class="table-cell">BLOUSE</div><div class="optional table-cell">ARMEDANGELS</div><div class="table-cell"><div style="background:#682464" class="label">GOTS_ORGANIC</div></div><div class="optional table-cell">94.99</div><div class="optional table-cell">EUR</div></a></div></div><button class="btn" onclick="\n    event.target.disabled = true;\n    setTimeout(function() {{\n        const stuff = event.target.parentNode.getElementsByClassName(&quot;hidden&quot;)[0];\n        const table = stuff.parentNode;\n        for(var i = 0; i &lt; 4 &amp;&amp; stuff.childNodes.length &gt; 0; i++) {{\n            const k = Math.floor(Math.random() * stuff.childNodes.length);\n            table.appendChild(stuff.childNodes[k]);\n        }}\n        event.target.disabled = stuff.childNodes.length == 0;\n    }}, 400);\n    ">more</button></div>',  # noqa
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
    category_cred_ratio = category_cred.pivot_table(
        "product_count", "category", "type", fill_value=0
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
        plot_category_cred=render_plotly_figure(plot_category_cred),
        stats=stats,
        excerpt=render_excerpt(get_relevant_products(db, 33)),
    )


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

@media (prefers-color-scheme: dark) {{
    body {{
        color: white;
        background: #131315;
    }}
    .container {{
        padding: 25px;
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

.label {{
    padding: 8px;
    margin: 2px;
    display: inline;
    border-radius: 3.5px;
}}

.stats {{
    font-size: 1.1em;
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

.product-link:nth-child(even) {{
    background: {webcolor(excerpt_hover)};
    box-shadow: inset 0px 2px 3px 0px {webcolor(map(shadow, excerpt_hover, excerpt))};
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
</html>""",
        minify_js=True,
        minify_css=True,
    )


if __name__ == "__main__":
    content = rebuild_landing_page()
    with open("../../index.html", "w", encoding="utf-8") as f:
        f.write(content)
