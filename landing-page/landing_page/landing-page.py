import re
from html import escape
from math import exp, log
from random import random
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plots
from minify_html import minify
from plotly import graph_objects as go
from plotly.io import to_html
from plotly.offline import get_plotlyjs
from sqlalchemy import desc, func, literal_column
from utils import Element, render_markdown, render_page, render_tag

from core.constants import ALL_SCRAPING_TABLE_NAMES
from core.domain import Product, ProductCategory
from database.connection import GreenDB, Scraping


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


def product2dict(product: Product) -> dict:
    labels = [re.sub(r"^certificate:", "", cert) for cert in product.sustainability_labels]
    return {
        key: labels if key == "labels" else getattr(product, key) for key in product_table_attribs
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


def get_relevant_products(self: GreenDB, count: int) -> List[Product]:
    """
    Fetch `count` products at random.

    Yields:
        Iterator[Product]: `Iterator` of domain object representation
    """
    with self._session_factory() as db_session:
        query = (
            db_session.query(self._database_class)
            .filter(self._database_class.sustainability_labels != ["certificate:OTHER"])
            .filter(self._database_class.sustainability_labels != ["certificate:UNKNOWN"])
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
            "plot_category_cred": '<div>                            <div id="3422f545-ff1c-45d4-8071-74a9acedce69" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("3422f545-ff1c-45d4-8071-74a9acedce69")) {                    Plotly.newPlot(                        "3422f545-ff1c-45d4-8071-74a9acedce69",                        [{"base":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9952121667292527,0.9939456841376925,0.9887640449438202,0.9887035443670377,0.9880665644843442,0.9779995571442128,0.9753208292201382,0.9711340206185567,0.9675480769230769,0.9428002534165988,0.9330143540669856,0.9266183687777518,0.8893205701312987,0.8726121485297275,0.8553191489361702,0.8523786096575577,0.8336745138178097,0.8330946128749901,0.8018607355720309,0.7921854577973447,0.7822736030828517,0.770014159677595,0.7690987483779145,0.7246312323403119,0.7084944751381216,0.6804105278214848,0.6776535216794193,0.5885350318471337,0.563953488372093,0.5448764800467768,0.5306748466257669,0.49019607843137253,0.4266666666666667,0.26666666666666666,0.1550062840385421],"name":"credible","offsetgroup":"1","x":["OVEN","STOVE","SMARTWATCH","COOKER_HOOD","TABLET","HEADSET","HEADPHONES","SWIMMWEAR","SWIMWEAR","DRYER","BAG","SNEAKERS","SHOES","SMARTPHONE","TRACKSUIT","LAPTOP","SOCKS","OVERALL","BACKPACK","DRESS","SKIRT","SHORTS","JACKET","SUIT","BLOUSE","JEANS","SWEATER","TOWEL","TOP","SHIRT","PANT","TSHIRT","PANTS","UNDERWEAR","WASHER","FRIDGE","NIGHTWEAR","DISHWASHER","FREEZER","TV","PRINTER","LINEN"],"y":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.004787833270747278,0.006054315862307559,0.011235955056179775,0.011296455632962336,0.011933435515655792,0.022000442855787176,0.024679170779861797,0.0288659793814433,0.03245192307692308,0.05719974658340121,0.06698564593301436,0.0733816312222482,0.11067942986870129,0.1273878514702726,0.14468085106382977,0.14762139034244226,0.16632548618219037,0.16690538712500994,0.19813926442796917,0.2078145422026553,0.21772639691714837,0.22998584032240496,0.23090125162208547,0.2753687676596881,0.2915055248618785,0.31958947217851524,0.3223464783205807,0.41146496815286626,0.436046511627907,0.4551235199532232,0.46932515337423314,0.5098039215686274,0.5733333333333334,0.7333333333333333,0.8449937159614579],"type":"bar"},{"name":"not credible","offsetgroup":"1","x":["OVEN","STOVE","SMARTWATCH","COOKER_HOOD","TABLET","HEADSET","HEADPHONES","SWIMMWEAR","SWIMWEAR","DRYER","BAG","SNEAKERS","SHOES","SMARTPHONE","TRACKSUIT","LAPTOP","SOCKS","OVERALL","BACKPACK","DRESS","SKIRT","SHORTS","JACKET","SUIT","BLOUSE","JEANS","SWEATER","TOWEL","TOP","SHIRT","PANT","TSHIRT","PANTS","UNDERWEAR","WASHER","FRIDGE","NIGHTWEAR","DISHWASHER","FREEZER","TV","PRINTER","LINEN"],"y":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9952121667292527,0.9939456841376925,0.9887640449438202,0.9887035443670377,0.9880665644843442,0.9779995571442128,0.9753208292201382,0.9711340206185567,0.9675480769230769,0.9428002534165988,0.9330143540669856,0.9266183687777518,0.8893205701312987,0.8726121485297275,0.8553191489361702,0.8523786096575577,0.8336745138178097,0.8330946128749901,0.8018607355720309,0.7921854577973447,0.7822736030828517,0.770014159677595,0.7690987483779145,0.7246312323403119,0.7084944751381216,0.6804105278214848,0.6776535216794193,0.5885350318471337,0.563953488372093,0.5448764800467768,0.5306748466257669,0.49019607843137253,0.4266666666666667,0.26666666666666666,0.1550062840385421],"type":"bar"}],                        {"title":{"text":"Normalized product count with vs. without credibility by category."},"yaxis":{"title":{"text":"credibility"}},"template":{"data":{"histogram2dcontour":[{"type":"histogram2dcontour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"choropleth":[{"type":"choropleth","colorbar":{"outlinewidth":0,"ticks":""}}],"histogram2d":[{"type":"histogram2d","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmap":[{"type":"heatmap","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmapgl":[{"type":"heatmapgl","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"contourcarpet":[{"type":"contourcarpet","colorbar":{"outlinewidth":0,"ticks":""}}],"contour":[{"type":"contour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"surface":[{"type":"surface","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"mesh3d":[{"type":"mesh3d","colorbar":{"outlinewidth":0,"ticks":""}}],"scatter":[{"fillpattern":{"fillmode":"overlay","size":10,"solidity":0.2},"type":"scatter"}],"parcoords":[{"type":"parcoords","line":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolargl":[{"type":"scatterpolargl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"scattergeo":[{"type":"scattergeo","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolar":[{"type":"scatterpolar","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"scattergl":[{"type":"scattergl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatter3d":[{"type":"scatter3d","line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattermapbox":[{"type":"scattermapbox","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterternary":[{"type":"scatterternary","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattercarpet":[{"type":"scattercarpet","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"pie":[{"automargin":true,"type":"pie"}]},"layout":{"autotypenumbers":"strict","colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"hovermode":"closest","hoverlabel":{"align":"left"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"bgcolor":"#E5ECF6","angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"ternary":{"bgcolor":"#E5ECF6","aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]]},"xaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"yaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"geo":{"bgcolor":"white","landcolor":"#E5ECF6","subunitcolor":"white","showland":true,"showlakes":true,"lakecolor":"white"},"title":{"x":0.05},"mapbox":{"style":"light"}}}},                        {"responsive": true}                    )                };                            </script>        </div>',  # noqa
            "stats": '<table>\n<thead>\n<tr>\n<th style="text-align:right"></th>\n<th style="text-align:left"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align:right"><strong>2023-01-13</strong></td>\n<td style="text-align:left">last updated</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>9,577,800</strong></td>\n<td style="text-align:left">pages scraped</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>724,007</strong></td>\n<td style="text-align:left">unique products</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>133,448</strong></td>\n<td style="text-align:left">unique credible products</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>41</strong></td>\n<td style="text-align:left">product categories</td>\n</tr>\n</tbody>\n</table>\n',  # noqa
            "excerpt": '<div class="excerpt"><div class="table-wrapper"><div class="table"><div class="hidden"><a href="https://www.zalando.de/organication-sweatjacke-bordeaux-orw21j01m-j11.html" class="table-row product-link"><div class="optional table-cell">JALE - Sweatjacke - bordeaux</div><div class="table-cell">JACKET</div><div class="optional table-cell">ORGANICATION</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">69.9</div><div class="optional table-cell">EUR</div></a><a href="https://www2.hm.com/fr_fr/productpage.0841434024.html" class="table-row product-link"><div class="optional table-cell">Robe T-shirt en coton</div><div class="table-cell">DRESS</div><div class="optional table-cell">H&M</div><div class="table-cell">HIGG_INDEX_MATERIALS</div><div class="optional table-cell">14.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/picard-luis-sac-a-dos-schwarz-pi351q00l-q11.html" class="table-row product-link"><div class="optional table-cell">LUIS - Sac à dos - schwarz</div><div class="table-cell">BAG</div><div class="optional table-cell">Picard</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">139.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/paul-green-baskets-basses-blau-paq11a0h1-k11.html" class="table-row product-link"><div class="optional table-cell">Baskets basses - blau</div><div class="table-cell">SHOES</div><div class="optional table-cell">Paul Green</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">93.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/creation-l-langarmshirt-shirt-1-tlg-1664886560/#variationId=1664886563" class="table-row product-link"><div class="optional table-cell">creation L Langarmshirt »Shirt« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">creation L</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www2.hm.com/fr_fr/productpage.1073567004.html" class="table-row product-link"><div class="optional table-cell">Pantalon jogger Relaxed Fit en coton</div><div class="table-cell">PANTS</div><div class="optional table-cell">H&M</div><div class="table-cell">HM_CONSCIOUS, OTHER</div><div class="optional table-cell">29.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/little-liffner-sprout-tote-cabas-dark-brown-l5l51h02u-o11.html" class="table-row product-link"><div class="optional table-cell">SPROUT TOTE - Cabas - dark brown</div><div class="table-cell">BAG</div><div class="optional table-cell">Little Liffner</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">495.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/copenhagen-cph775-baskets-basses-light-grey-coy11a03u-c11.html" class="table-row product-link"><div class="optional table-cell">CPH775  - Baskets basses - light grey</div><div class="table-cell">SHOES</div><div class="optional table-cell">Copenhagen</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">76.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/paul-smith-washbag-unisex-trousse-de-toilette-blackmulti-coloured-ps954h00u-q11.html" class="table-row product-link"><div class="optional table-cell">WASHBAG UNISEX - Trousse de toilette - black/multi-coloured</div><div class="table-cell">BAG</div><div class="optional table-cell">Paul Smith</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">255.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wunderwerk-regular-fit-jeans-phil-denim-S0K2Y061/#variationId=S0K2Y061LBSA" class="table-row product-link"><div class="optional table-cell">wunderwerk Regular-fit-Jeans »Phil denim«</div><div class="table-cell">PANTS</div><div class="optional table-cell">wunderwerk</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">119.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/authentic-le-jogger-pyjama-2-tlg-in-langer-form-536281856/#variationId=536867255" class="table-row product-link"><div class="optional table-cell">AUTHENTIC LE JOGGER Pyjama (2 tlg) in langer Form</div><div class="table-cell">NIGHTWEAR</div><div class="optional table-cell">AUTHENTIC LE JOGGER</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">26.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/felmini-gerbera-santiags-lavado-fe211a02b-o11.html" class="table-row product-link"><div class="optional table-cell">GERBERA - Santiags - lavado</div><div class="table-cell">SHOES</div><div class="optional table-cell">Felmini</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">140.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/deuter-rucksack-S0655034/#variationId=S0655034ADW3" class="table-row product-link"><div class="optional table-cell">deuter Rucksack</div><div class="table-cell">BACKPACK</div><div class="optional table-cell">deuter</div><div class="table-cell">BLUESIGN_PRODUCT, GREEN_BUTTON</div><div class="optional table-cell">160.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/veja-campo-sneaker-low-steelnautico-vj212o02m-k11.html" class="table-row product-link"><div class="optional table-cell">CAMPO - Sneaker low - steel/nautico</div><div class="table-cell">SHOES</div><div class="optional table-cell">Veja</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">129.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/camper-tws-baskets-basses-beige-ca312o0ba-b11.html" class="table-row product-link"><div class="optional table-cell">RUNNER TWINS - Baskets basses - beige</div><div class="table-cell">SNEAKERS</div><div class="optional table-cell">Camper</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">69.0</div><div class="optional table-cell">EUR</div></a><a href="https://www2.hm.com/fr_fr/productpage.1111197001.html" class="table-row product-link"><div class="optional table-cell">Blazer à fermeture droite</div><div class="table-cell">JACKET</div><div class="optional table-cell">H&M</div><div class="table-cell">HM_CONSCIOUS</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/camper-runner-4-baskets-basses-ca312b03g-o11.html" class="table-row product-link"><div class="optional table-cell">RUNNER FOUR - Baskets basses - medium brown</div><div class="table-cell">SHOES</div><div class="optional table-cell">Camper</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">130.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/vagabond-harvey-schnuerer-black-va112m00k-q11.html" class="table-row product-link"><div class="optional table-cell">HARVEY - Business-Schnürer - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Vagabond</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">139.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.asos.com/fr/monki/monki-yoko-pantalon-large-en-velours-cotele-beige/prd/201304014" class="table-row product-link"><div class="optional table-cell">Monki - Yoko - Pantalon large en velours côtelé - Beige</div><div class="table-cell">PANT</div><div class="optional table-cell">Monki</div><div class="table-cell">BETTER_COTTON_INITIATIVE</div><div class="optional table-cell">36.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-3-4-arm-pullover-pullover-1550566341/#variationId=1550566347" class="table-row product-link"><div class="optional table-cell">Classic 3/4 Arm-Pullover »Pullover«</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Classic</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/the-north-face-retro-nuptse-vest-veste-sans-manches-fuschia-pink-th322t00s-j11.html" class="table-row product-link"><div class="optional table-cell">RETRO NUPTSE VEST - Veste sans manches - fuschia pink</div><div class="table-cell">JACKET</div><div class="optional table-cell">The North Face</div><div class="table-cell">RESPONSIBLE_DOWN_STANDARD</div><div class="optional table-cell">264.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/refill-by-shoeby-short-en-jean-blue-r3i22f00j-k11.html" class="table-row product-link"><div class="optional table-cell">Short en jean - blue</div><div class="table-cell">JEANS</div><div class="optional table-cell">Refill by Shoeby</div><div class="table-cell">ORGANIC_CONTENT_STANDARD_BLENDED</div><div class="optional table-cell">54.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-t-shirt-imprime-black-h3a21d34j-q11.html" class="table-row product-link"><div class="optional table-cell">AVENGERS CLASSIC CAP MARVEL - T-shirt imprimé - black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">31.49</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/camperlab-peu-stadium-sneaker-low-rosa-cko12o002-j11.html" class="table-row product-link"><div class="optional table-cell">STADIUM - Sneaker low - rosa</div><div class="table-cell">SHOES</div><div class="optional table-cell">CAMPERLAB</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">120.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/les-petits-basics-vivre-d-amour-unisex-t-shirt-print-navy-l4z210014-k11.html" class="table-row product-link"><div class="optional table-cell">VIVRE D AMOUR UNISEX - T-Shirt print - navy</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Les Petits Basics</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">21.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.asos.com/fr/asos-design/asos-design-salopette-en-jean-style-baggy-noir/prd/201122817" class="table-row product-link"><div class="optional table-cell">ASOS DESIGN - Salopette en jean style baggy - Noir</div><div class="table-cell">PANT</div><div class="optional table-cell">ASOS DESIGN</div><div class="table-cell">BETTER_COTTON_INITIATIVE</div><div class="optional table-cell">62.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/marc-opolo-long-sleeved-top-brushed-peach-ma321d15v-h12.html" class="table-row product-link"><div class="optional table-cell">Long sleeved top - brushed peach</div><div class="table-cell">SOCKS</div><div class="optional table-cell">Marc O\'Polo</div><div class="table-cell">ORGANIC_CONTENT_STANDARD_100</div><div class="optional table-cell">23.0</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.co.uk/massimo-dutti-tote-bag-brown-m3i51h09s-o11.html" class="table-row product-link"><div class="optional table-cell">PLAITED - Tote bag - brown</div><div class="table-cell">SOCKS</div><div class="optional table-cell">Massimo Dutti</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">369.0</div><div class="optional table-cell">GBP</div></a></div><div class="table-row"><div class="optional table-header">name</div><div class="table-header">category</div><div class="optional table-header">brand</div><div class="table-header">labels</div><div class="optional table-header">price</div><div class="optional table-header">currency</div></div><a href="https://www.zalando.de/tommy-jeans-archive-basket-sneaker-low-white-tob12o05a-a11.html" class="table-row product-link"><div class="optional table-cell">ARCHIVE BASKET - Sneaker low - white</div><div class="table-cell">SNEAKERS</div><div class="optional table-cell">Tommy Jeans</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">109.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/camper-peu-stadium-sneaker-low-weiss-ca312n01z-a12.html" class="table-row product-link"><div class="optional table-cell">PEU STADIUM - Sneaker low - weiß</div><div class="table-cell">SNEAKERS</div><div class="optional table-cell">Camper</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">145.0</div><div class="optional table-cell">EUR</div></a><a href="https://www2.hm.com/fr_fr/productpage.1022027005.html" class="table-row product-link"><div class="optional table-cell">Haut de maillot paddé avec liens à nouer</div><div class="table-cell">SWIMWEAR</div><div class="optional table-cell">H&M</div><div class="table-cell">HM_CONSCIOUS</div><div class="optional table-cell">5.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/hvisk-handtasche-amble-twill-recycled-small-S0J2S062/#variationId=S0J2S06219NZ" class="table-row product-link"><div class="optional table-cell">HVISK Handtasche »AMBLE TWILL RECYCLED SMALL«</div><div class="table-cell">BAG</div><div class="optional table-cell">HVISK</div><div class="table-cell">GLOBAL_RECYCLED_STANDARD</div><div class="optional table-cell">89.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.asos.com/fr/asos-design/asos-design-body-a-dos-nageur-vert-sauge/prd/201766451" class="table-row product-link"><div class="optional table-cell">ASOS DESIGN - Body à dos nageur - Vert sauge</div><div class="table-cell">TOP</div><div class="optional table-cell">ASOS DESIGN</div><div class="table-cell">BETTER_COTTON_INITIATIVE</div><div class="optional table-cell">15.99</div><div class="optional table-cell">EUR</div></a></div></div><button class="btn" onclick="\n    event.target.disabled = true;\n    setTimeout(function() {{\n        const stuff = event.target.parentNode.getElementsByClassName(&quot;hidden&quot;)[0];\n        const table = stuff.parentNode;\n        for(var i = 0; i &lt; 4 &amp;&amp; stuff.childNodes.length &gt; 0; i++) {{\n            const k = Math.floor(Math.random() * stuff.childNodes.length);\n            table.appendChild(stuff.childNodes[k]);\n        }}\n        event.target.disabled = stuff.childNodes.length == 0;\n    }}, 400);\n    ">more</button></div>',  # noqa
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
        f"""
| | |
| -: | :- |
| **{products_per_country["latest_extraction_timestamp"]}** | last updated |
| **{total_scrapes:,}** | pages scraped |
| **{products_per_cred['all_unique_product_count']:,}** | unique products |
| **{products_per_cred['unique_credible_product_count']:,}** | unique credible products |
| **{len(all_categories)}** | product categories |"""
    )

    category_cred = get_cred_by_category(db)
    category_cred_ratio = category_cred.pivot_table(
        "product_count", "category", "type", fill_value=0
    )
    category_cred_ratio = category_cred_ratio.div(category_cred_ratio.sum(1), 0).sort_values(
        "credible"
    )

    plot_category_cred = go.Figure(
        data=[
            go.Bar(
                name="credible",
                x=category_cred_ratio.index,
                y=category_cred_ratio["credible"],
                offsetgroup=1,
                base=category_cred_ratio["not_credible"],
            ),
            go.Bar(
                name="not credible",
                x=category_cred_ratio.index,
                y=category_cred_ratio["not_credible"],
                offsetgroup=1,
            ),
        ],
        layout=go.Layout(
            title="Normalized product count with vs. without credibility by category.",
            yaxis_title="credibility",
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
        padding: 15px;
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
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
