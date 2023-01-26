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
from sqlalchemy import desc, func, literal_column, or_
from utils import Element, render_markdown, render_page, render_tag

from core.constants import ALL_SCRAPING_TABLE_NAMES
from core.domain import Product, ProductCategory

# from core.sustainability_labels.bootstrap_database import sustainability_labels
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


def kurgel(s: float) -> float:
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
    return re.sub(r"^certificate:", "", label)


def product2dict(product: Product) -> dict:
    labels = [render_label(label) for label in product.sustainability_labels]
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
            "plot_category_cred": '<div>                            <div id="22d822e7-8e13-4e1e-b134-cbdca176d26a" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("22d822e7-8e13-4e1e-b134-cbdca176d26a")) {                    Plotly.newPlot(                        "22d822e7-8e13-4e1e-b134-cbdca176d26a",                        [{"name":"not credible","x":["TABLET","SMARTWATCH","HEADSET","HEADPHONES","OVEN","COOKER_HOOD","STOVE","SWIMMWEAR","SWIMWEAR","BAG","SNEAKERS","SHOES","SMARTPHONE","TRACKSUIT","LAPTOP","DRYER","SOCKS","BACKPACK","OVERALL","DRESS","SKIRT","SUIT","JACKET","SHORTS","BLOUSE","TOWEL","JEANS","SWEATER","SHIRT","TOP","UNDERWEAR","PANT","TSHIRT","PANTS","FRIDGE","WASHER","NIGHTWEAR","DISHWASHER","FREEZER","PRINTER","LINEN","TV"],"y":[1042,264,48,5315,417,396,247,10890,5754,36076,9060,74633,1632,1914,4008,232,20732,4068,2703,39086,8414,1886,58584,3418,21500,4493,17004,58829,96171,14210,42056,33544,29917,19809,198,468,7940,174,50,276,404,34],"type":"bar"},{"name":"credible","x":["TABLET","SMARTWATCH","HEADSET","HEADPHONES","OVEN","COOKER_HOOD","STOVE","SWIMMWEAR","SWIMWEAR","BAG","SNEAKERS","SHOES","SMARTPHONE","TRACKSUIT","LAPTOP","DRYER","SOCKS","BACKPACK","OVERALL","DRESS","SKIRT","SUIT","JACKET","SHORTS","BLOUSE","TOWEL","JEANS","SWEATER","SHIRT","TOP","UNDERWEAR","PANT","TSHIRT","PANTS","FRIDGE","WASHER","NIGHTWEAR","DISHWASHER","FREEZER","PRINTER","LINEN","TV"],"y":[0,0,0,0,0,0,0,55,43,417,107,1416,32,45,105,8,1325,308,223,4852,1219,328,10381,628,4350,1106,4410,15642,28898,4342,13983,12424,13580,9453,132,345,6554,153,71,761,2257,681],"type":"bar"}],                        {"barmode":"stack","barnorm":"fraction","title":{"text":"Normalized product count with vs. without credibility by category."},"yaxis":{"title":{"text":"credibility"}},"template":{"data":{"histogram2dcontour":[{"type":"histogram2dcontour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"choropleth":[{"type":"choropleth","colorbar":{"outlinewidth":0,"ticks":""}}],"histogram2d":[{"type":"histogram2d","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmap":[{"type":"heatmap","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmapgl":[{"type":"heatmapgl","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"contourcarpet":[{"type":"contourcarpet","colorbar":{"outlinewidth":0,"ticks":""}}],"contour":[{"type":"contour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"surface":[{"type":"surface","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"mesh3d":[{"type":"mesh3d","colorbar":{"outlinewidth":0,"ticks":""}}],"scatter":[{"fillpattern":{"fillmode":"overlay","size":10,"solidity":0.2},"type":"scatter"}],"parcoords":[{"type":"parcoords","line":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolargl":[{"type":"scatterpolargl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"scattergeo":[{"type":"scattergeo","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolar":[{"type":"scatterpolar","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"scattergl":[{"type":"scattergl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatter3d":[{"type":"scatter3d","line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattermapbox":[{"type":"scattermapbox","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterternary":[{"type":"scatterternary","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattercarpet":[{"type":"scattercarpet","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"pie":[{"automargin":true,"type":"pie"}]},"layout":{"autotypenumbers":"strict","colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"hovermode":"closest","hoverlabel":{"align":"left"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"bgcolor":"#E5ECF6","angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"ternary":{"bgcolor":"#E5ECF6","aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]]},"xaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"yaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"geo":{"bgcolor":"white","landcolor":"#E5ECF6","subunitcolor":"white","showland":true,"showlakes":true,"lakecolor":"white"},"title":{"x":0.05},"mapbox":{"style":"light"}}}},                        {"responsive": true}                    )                };                            </script>        </div>',  # noqa
            "stats": '<table>\n<thead>\n<tr>\n<th style="text-align:right"></th>\n<th style="text-align:left"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align:right"><strong>2023-01-20</strong></td>\n<td style="text-align:left">last updated</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>9,936,634</strong></td>\n<td style="text-align:left">pages scraped</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>778,392</strong></td>\n<td style="text-align:left">unique products</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>140,632</strong></td>\n<td style="text-align:left">unique products with credible sustainability labels</td>\n</tr>\n<tr>\n<td style="text-align:right"><strong>41</strong></td>\n<td style="text-align:left">product categories</td>\n</tr>\n</tbody>\n</table>\n',  # noqa
            "excerpt": '<div class="excerpt"><div class="table-wrapper"><div class="table"><div class="hidden"><a href="https://www.zalando.de/snocks-3-pack-unterhemd-shirt-weiss-sne82q001-a11.html" class="table-row product-link"><div class="optional table-cell">V-NECK - 3 PACK - Unterhemd/-shirt - weiß</div><div class="table-cell">JACKET</div><div class="optional table-cell">SNOCKS</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">26.24</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/armedangels-sweatshirt-eminaa-color-block-damen-1-tlg-S024Q09P/#variationId=S024Q09PB49B" class="table-row product-link"><div class="optional table-cell">Armedangels Sweatshirt »EMINAA COLOR BLOCK Damen« (1-tlg)</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Armedangels</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">99.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/h-i-s-langarmshirt-packung-2-tlg-2er-pack-1388287085/#variationId=1388281263" class="table-row product-link"><div class="optional table-cell">H.I.S Langarmshirt (Packung, 2-tlg., 2er-Pack)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">H.I.S</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/hanseatic-gefrierschrank-hgs8555ci-85-cm-hoch-55-cm-breit-706311767/#variationId=1116266358" class="table-row product-link"><div class="optional table-cell">Hanseatic Gefrierschrank HGS8555CI, 85 cm hoch, 55 cm breit</div><div class="table-cell">FREEZER</div><div class="optional table-cell">Hanseatic</div><div class="table-cell">EU_ENERGY_LABEL_C, OTHER</div><div class="optional table-cell">279.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/ambria-rundhalsshirt-shirt-1-tlg-889926385/#variationId=889949612" class="table-row product-link"><div class="optional table-cell">Ambria Rundhalsshirt »Shirt« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Ambria</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">19.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/lascana-kurzjacke-mit-modischem-karomuster-1235994954/#variationId=1235995049" class="table-row product-link"><div class="optional table-cell">LASCANA Kurzjacke mit modischem Karomuster</div><div class="table-cell">JACKET</div><div class="optional table-cell">LASCANA</div><div class="table-cell">COTTON_MADE_IN_AFRICA, OTHER</div><div class="optional table-cell">69.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/aniston-casual-jerseykleid-mit-tunnelzug-in-der-taille-709786997/#variationId=709797096" class="table-row product-link"><div class="optional table-cell">Aniston CASUAL Jerseykleid mit Tunnelzug in der Taille</div><div class="table-cell">DRESS</div><div class="optional table-cell">Aniston CASUAL</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">19.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/feel-good-relaxhose-1137939798/#variationId=889924274" class="table-row product-link"><div class="optional table-cell">feel good Relaxhose</div><div class="table-cell">PANTS</div><div class="optional table-cell">feel good</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-dancer-1-tlg-S0Z1C049/#variationId=S0Z1C0493VKT" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Dancer« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">15.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/ashley-brooke-by-heine-druckkleid-druck-kleid-1589836068/#variationId=1589836070" class="table-row product-link"><div class="optional table-cell">ASHLEY BROOKE by Heine Druckkleid »Druck-Kleid«</div><div class="table-cell">DRESS</div><div class="optional table-cell">ASHLEY BROOKE by Heine</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">79.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/h-i-s-sweatshirt-mit-kleinem-retro-print-1176760546/#variationId=1176761365" class="table-row product-link"><div class="optional table-cell">H.I.S Sweatshirt mit kleinem Retro-Print</div><div class="table-cell">SWEATER</div><div class="optional table-cell">H.I.S</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">29.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-dachs-1-tlg-S014505P/#variationId=S014505PY5KW" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Dachs« (1-tlg)</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">34.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/kangaroos-t-shirt-mit-fotomotiv-und-pailletten-schriftzug-1437802940/#variationId=1410236210" class="table-row product-link"><div class="optional table-cell">KangaROOS T-Shirt mit Fotomotiv und Pailletten-Schriftzug</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">KangaROOS</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/olymp-businesshemd-olymp-luxor-modern-fit-S053O0ML/#variationId=S053O0MLD89A" class="table-row product-link"><div class="optional table-cell">OLYMP Businesshemd »OLYMP Luxor modern fit«</div><div class="table-cell">SHIRT</div><div class="optional table-cell">OLYMP</div><div class="table-cell">MADE_IN_GREEN_OEKO_TEX</div><div class="optional table-cell">44.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/armedangels-jeans-shorts-farrow-ar321s00o-c11.html" class="table-row product-link"><div class="optional table-cell">SILVAA - Jeans Shorts - farrow</div><div class="table-cell">JEANS</div><div class="optional table-cell">ARMEDANGELS</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">59.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/jack-wolfskin-daypack-savona-de-luxe-1613762102/#variationId=1613765951" class="table-row product-link"><div class="optional table-cell">Jack Wolfskin Daypack »SAVONA DE LUXE«</div><div class="table-cell">BACKPACK</div><div class="optional table-cell">Jack Wolfskin</div><div class="table-cell">BLUESIGN_PRODUCT, GREEN_BUTTON, OTHER</div><div class="optional table-cell">59.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-lieblingsonkel-1-tlg-S0Z1C07P/#variationId=S0Z1C07PZETY" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Lieblingsonkel« (1-tlg)</div><div class="table-cell">SHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">29.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-basics-kurzarmshirt-2-in-1-shirt-1-tlg-1600267178/#variationId=1600276048" class="table-row product-link"><div class="optional table-cell">Classic Basics Kurzarmshirt »2-in-1-Shirt« (1-tlg)</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Classic Basics</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">10.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-basics-jerseyrock-1692820931/#variationId=1692820996" class="table-row product-link"><div class="optional table-cell">Classic Basics Jerseyrock</div><div class="table-cell">SKIRT</div><div class="optional table-cell">Classic Basics</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">20.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-t-shirt-imprime-black-h3a2101vt-q11.html" class="table-row product-link"><div class="optional table-cell">DNCA LIP EMBROIDERY UNISEX - T-shirt imprimé - black</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">31.49</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-sweatshirt-black-h3a21019d-q11.html" class="table-row product-link"><div class="optional table-cell">Sweatshirt - black</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">50.39</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/henry-tiger-t-shirt-imprime-red-h3a21d2xb-g11.html" class="table-row product-link"><div class="optional table-cell">DISNEY WINNIE THE POOH POOH FASHION - T-shirt imprimé - red</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">31.49</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/ashley-brooke-by-heine-hemdbluse-1687147563/#variationId=1687147568" class="table-row product-link"><div class="optional table-cell">ASHLEY BROOKE by Heine Hemdbluse</div><div class="table-cell">BLOUSE</div><div class="optional table-cell">Ashley Brooke by heine</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/arizona-jeansjeggings-high-waist-1171279533/#variationId=1171281753" class="table-row product-link"><div class="optional table-cell">Arizona Jeansjeggings High Waist</div><div class="table-cell">PANTS</div><div class="optional table-cell">Arizona</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/aniston-casual-t-shirt-im-marine-look-1136594514/#variationId=1136594531" class="table-row product-link"><div class="optional table-cell">Aniston CASUAL T-Shirt im Marine-Look</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Aniston CASUAL</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">17.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/organication-sweatjacke-mint-blue-orw210006-m11.html" class="table-row product-link"><div class="optional table-cell">Sweatjacke - mint blue</div><div class="table-cell">JACKET</div><div class="optional table-cell">ORGANICATION</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">59.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-gschmarri-1-tlg-S0Z1C046/#variationId=S0Z1C046291G" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Gschmarri« (1-tlg)</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">29.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/ulla-popken-langarmshirt-efeugruen-up121d1ev-t11.html" class="table-row product-link"><div class="optional table-cell">Langarmshirt - efeugrün</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Ulla Popken</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">39.99</div><div class="optional table-cell">EUR</div></a></div><div class="table-row"><div class="optional table-header">name</div><div class="table-header">category</div><div class="optional table-header">brand</div><div class="table-header">labels</div><div class="optional table-header">price</div><div class="optional table-header">currency</div></div><a href="https://www.otto.de/p/wunderwerk-t-shirt-core-tee-S093W0MN/#variationId=S093W0MN1B2T" class="table-row product-link"><div class="optional table-cell">wunderwerk T-Shirt »Core tee«</div><div class="table-cell">SHIRT</div><div class="optional table-cell">wunderwerk</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">49.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/lascana-panty-3-stueck-mit-grafischer-spitze-868845816/#variationId=928679183" class="table-row product-link"><div class="optional table-cell">LASCANA Panty (3 Stück) mit grafischer Spitze</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">LASCANA</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">19.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/bettwaesche-poupy-casatex-moderne-ornamentik-1219238769/#variationId=1211128303" class="table-row product-link"><div class="optional table-cell">Bettwäsche »Poupy«, CASATEX, moderne Ornamentik</div><div class="table-cell">LINEN</div><div class="optional table-cell">CASATEX</div><div class="table-cell">MADE_IN_GREEN_OEKO_TEX</div><div class="optional table-cell">41.98</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/henry-tiger-t-shirt-print-melange-grey-h3a21d17e-c11.html" class="table-row product-link"><div class="optional table-cell">POCAHONTAS POCA BIRTHDAY 16 - T-Shirt print - melange grey</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Henry Tiger</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">28.79</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-find-your-wild-1-tlg-S0145052/#variationId=S01450528TWH" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Find your wild« (1-tlg)</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">34.9</div><div class="optional table-cell">EUR</div></a></div></div><button class="btn" onclick="\n    event.target.disabled = true;\n    setTimeout(function() {{\n        const stuff = event.target.parentNode.getElementsByClassName(&quot;hidden&quot;)[0];\n        const table = stuff.parentNode;\n        for(var i = 0; i &lt; 4 &amp;&amp; stuff.childNodes.length &gt; 0; i++) {{\n            const k = Math.floor(Math.random() * stuff.childNodes.length);\n            table.appendChild(stuff.childNodes[k]);\n        }}\n        event.target.disabled = stuff.childNodes.length == 0;\n    }}, 400);\n    ">more</button></div>',  # noqa
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
