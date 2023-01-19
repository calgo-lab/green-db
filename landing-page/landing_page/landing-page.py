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
            "plot_category_cred": '<div>                            <div id="35dae09d-cc9f-41b3-a72d-2d7b6a2e70ab" class="plotly-graph-div" style="height:100%; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("35dae09d-cc9f-41b3-a72d-2d7b6a2e70ab")) {                    Plotly.newPlot(                        "35dae09d-cc9f-41b3-a72d-2d7b6a2e70ab",                        [{"base":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9956160805894972,0.9941972920696325,0.9890002178174689,0.9888505811043764,0.9832402234636871,0.9778811467628631,0.9768160741885626,0.9745347698334965,0.9660678642714571,0.9434090292228354,0.9294805641554867,0.9285377358490566,0.8904858725373344,0.8724983860555197,0.8533626360571998,0.8523878437047757,0.8364389233954451,0.8326702737110121,0.8016820532650201,0.7917369887073094,0.785331331760669,0.76979280261723,0.7691024609401194,0.7255957811352662,0.6963851036239962,0.6785829307568438,0.6770631395548575,0.5868852459016394,0.5809399477806788,0.544748791562912,0.5324675324675324,0.42857142857142855,0.4266666666666667,0.2627450980392157,0.15635451505016723],"name":"credible","offsetgroup":"1","x":["TABLET","SMARTWATCH","HEADSET","HEADPHONES","OVEN","COOKER_HOOD","STOVE","SWIMMWEAR","SWIMWEAR","SNEAKERS","BAG","DRYER","SHOES","TRACKSUIT","SMARTPHONE","LAPTOP","SOCKS","OVERALL","BACKPACK","DRESS","SKIRT","JACKET","SHORTS","SUIT","BLOUSE","JEANS","SWEATER","TOWEL","TOP","SHIRT","PANT","TSHIRT","PANTS","UNDERWEAR","FRIDGE","WASHER","NIGHTWEAR","DISHWASHER","FREEZER","TV","PRINTER","LINEN"],"y":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.004383919410502752,0.005802707930367505,0.010999782182531039,0.011149418895623644,0.01675977653631285,0.02211885323713689,0.023183925811437404,0.025465230166503428,0.033932135728542916,0.05659097077716457,0.07051943584451324,0.0714622641509434,0.10951412746266564,0.1275016139444803,0.1466373639428003,0.1476121562952243,0.16356107660455488,0.1673297262889879,0.19831794673497993,0.20826301129269062,0.2146686682393309,0.2302071973827699,0.23089753905988064,0.27440421886473376,0.3036148963760038,0.3214170692431562,0.32293686044514247,0.4131147540983607,0.41906005221932113,0.45525120843708805,0.4675324675324675,0.5714285714285714,0.5733333333333334,0.7372549019607844,0.8436454849498328],"type":"bar"},{"name":"not credible","offsetgroup":"1","x":["TABLET","SMARTWATCH","HEADSET","HEADPHONES","OVEN","COOKER_HOOD","STOVE","SWIMMWEAR","SWIMWEAR","SNEAKERS","BAG","DRYER","SHOES","TRACKSUIT","SMARTPHONE","LAPTOP","SOCKS","OVERALL","BACKPACK","DRESS","SKIRT","JACKET","SHORTS","SUIT","BLOUSE","JEANS","SWEATER","TOWEL","TOP","SHIRT","PANT","TSHIRT","PANTS","UNDERWEAR","FRIDGE","WASHER","NIGHTWEAR","DISHWASHER","FREEZER","TV","PRINTER","LINEN"],"y":[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9956160805894972,0.9941972920696325,0.9890002178174689,0.9888505811043764,0.9832402234636871,0.9778811467628631,0.9768160741885626,0.9745347698334965,0.9660678642714571,0.9434090292228354,0.9294805641554867,0.9285377358490566,0.8904858725373344,0.8724983860555197,0.8533626360571998,0.8523878437047757,0.8364389233954451,0.8326702737110121,0.8016820532650201,0.7917369887073094,0.785331331760669,0.76979280261723,0.7691024609401194,0.7255957811352662,0.6963851036239962,0.6785829307568438,0.6770631395548575,0.5868852459016394,0.5809399477806788,0.544748791562912,0.5324675324675324,0.42857142857142855,0.4266666666666667,0.2627450980392157,0.15635451505016723],"type":"bar"}],                        {"title":{"text":"Normalized product count with vs. without credibility by category."},"yaxis":{"title":{"text":"credibility"}},"template":{"data":{"histogram2dcontour":[{"type":"histogram2dcontour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"choropleth":[{"type":"choropleth","colorbar":{"outlinewidth":0,"ticks":""}}],"histogram2d":[{"type":"histogram2d","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmap":[{"type":"heatmap","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"heatmapgl":[{"type":"heatmapgl","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"contourcarpet":[{"type":"contourcarpet","colorbar":{"outlinewidth":0,"ticks":""}}],"contour":[{"type":"contour","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"surface":[{"type":"surface","colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]}],"mesh3d":[{"type":"mesh3d","colorbar":{"outlinewidth":0,"ticks":""}}],"scatter":[{"fillpattern":{"fillmode":"overlay","size":10,"solidity":0.2},"type":"scatter"}],"parcoords":[{"type":"parcoords","line":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolargl":[{"type":"scatterpolargl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"scattergeo":[{"type":"scattergeo","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterpolar":[{"type":"scatterpolar","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"scattergl":[{"type":"scattergl","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatter3d":[{"type":"scatter3d","line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattermapbox":[{"type":"scattermapbox","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scatterternary":[{"type":"scatterternary","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"scattercarpet":[{"type":"scattercarpet","marker":{"colorbar":{"outlinewidth":0,"ticks":""}}}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"pie":[{"automargin":true,"type":"pie"}]},"layout":{"autotypenumbers":"strict","colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"hovermode":"closest","hoverlabel":{"align":"left"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"bgcolor":"#E5ECF6","angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"ternary":{"bgcolor":"#E5ECF6","aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]]},"xaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"yaxis":{"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","automargin":true,"zerolinewidth":2},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white","gridwidth":2}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"geo":{"bgcolor":"white","landcolor":"#E5ECF6","subunitcolor":"white","showland":true,"showlakes":true,"lakecolor":"white"},"title":{"x":0.05},"mapbox":{"style":"light"}}}},                        {"responsive": true}                    )                };                            </script>        </div>',  # noqa
            "stats": '<table>\n<thead>\n<tr>\n<th style="text-align:right"></th>\n<th style="text-align:left"></th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td style="text-align:right">last updated</td>\n<td style="text-align:left"><strong>2023-01-13</strong></td>\n</tr>\n<tr>\n<td style="text-align:right">pages scraped</td>\n<td style="text-align:left"><strong>9,577,800</strong></td>\n</tr>\n<tr>\n<td style="text-align:right">unique products</td>\n<td style="text-align:left"><strong>724,666</strong></td>\n</tr>\n<tr>\n<td style="text-align:right">unique credible products</td>\n<td style="text-align:left"><strong>133,708</strong></td>\n</tr>\n<tr>\n<td style="text-align:right">product categories</td>\n<td style="text-align:left"><strong>41</strong></td>\n</tr>\n</tbody>\n</table>\n',  # noqa
            "excerpt": '<div class="excerpt"><div class="table-wrapper"><div class="table"><div class="hidden"><a href="https://www.zalando.co.uk/tiger-of-sweden-salasi-trainers-ti511a00r-q11.html" class="table-row product-link"><div class="optional table-cell">SALASI - Trainers - black</div><div class="table-cell">SOCKS</div><div class="optional table-cell">Tiger of Sweden</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">229.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.otto.de/p/classic-basics-caprileggings-1600281852/#variationId=1600281853" class="table-row product-link"><div class="optional table-cell">Classic Basics Caprileggings</div><div class="table-cell">PANT</div><div class="optional table-cell">Classic Basics</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">15.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/selected-homme-slhchristopher-wallabee-casual-lace-ups-black-se612m02d-q11.html" class="table-row product-link"><div class="optional table-cell">SLHCHRISTOPHER WALLABEE  - Casual lace-ups - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Selected Homme</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">63.0</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.co.uk/pavement-jamie-long-winter-boots-black-pv111x00e-q11.html" class="table-row product-link"><div class="optional table-cell">JAMIE LONG - Winter boots - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Pavement</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">154.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.de/blissker-omega-stripes-sweatshirt-weiss-bkd210002-a11.html" class="table-row product-link"><div class="optional table-cell">OMEGA STRIPES - Kapuzenpullover - weiss</div><div class="table-cell">SWEATER</div><div class="optional table-cell">Blissker</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">200.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/tommy-hilfiger-outdoor-boot-bottines-desert-sky-to111n07s-k11.html" class="table-row product-link"><div class="optional table-cell">OUTDOOR BOOT - Bottines à talons hauts - desert sky</div><div class="table-cell">SHOES</div><div class="optional table-cell">Tommy Hilfiger</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">95.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/marc-opolo-longsleeve-v-neck-strickjacke-chalky-sand-ma321i12t-b11.html" class="table-row product-link"><div class="optional table-cell">LONGSLEEVE V NECK - Strickjacke - chalky sand</div><div class="table-cell">JACKET</div><div class="optional table-cell">Marc O\'Polo</div><div class="table-cell">RESPONSIBLE_WOOL_STANDARD</div><div class="optional table-cell">75.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/samsoee-samsoee-joel-t-shirt-basique-urban-chic-sa322o041-p11.html" class="table-row product-link"><div class="optional table-cell">JOEL - T-shirt basique - urban chic</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Samsøe Samsøe</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">64.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/classic-basics-caprihose-1692816835/#variationId=1692816914" class="table-row product-link"><div class="optional table-cell">Classic Basics Caprihose</div><div class="table-cell">PANTS</div><div class="optional table-cell">Classic Basics</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">18.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/toni-pons-espadrille-cognac-t1m11e00q-o11.html" class="table-row product-link"><div class="optional table-cell">Keilsandalette - cognac</div><div class="table-cell">SHOES</div><div class="optional table-cell">Toni Pons</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">64.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/merrell-vapor-glove-3-luna-laufschuh-natural-running-stonewash-me141a0ag-k11.html" class="table-row product-link"><div class="optional table-cell">VAPOR GLOVE 3 LUNA  - Laufschuh Natural running - stonewash</div><div class="table-cell">SHOES</div><div class="optional table-cell">Merrell</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">95.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/g-star-triple-straight-jean-droit-faded-hague-blue-gs122g0wa-k11.html" class="table-row product-link"><div class="optional table-cell">TRIPLE STRAIGHT - Jean droit - faded hague blue</div><div class="table-cell">JEANS</div><div class="optional table-cell">G-Star</div><div class="table-cell">CRADLE_TO_CRADLE_GOLD</div><div class="optional table-cell">129.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/zign-pantolette-hoch-blue-zi111a0lp-k11.html" class="table-row product-link"><div class="optional table-cell">LEATHER - Pantolette hoch - blue</div><div class="table-cell">SHOES</div><div class="optional table-cell">Zign</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">47.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/bench-sweathose-in-7-8-laenge-979380757/#variationId=979383008" class="table-row product-link"><div class="optional table-cell">Bench. Sweathose in 7/8-Länge</div><div class="table-cell">PANT</div><div class="optional table-cell">Bench.</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">29.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/natural-vibes-accesoires-tech-black-nax81000u-q11.html" class="table-row product-link"><div class="optional table-cell">BIO SOCKEN MID CUT 3 PACK - Chaussettes - black</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">Natural Vibes</div><div class="table-cell">GOTS_MADE_WITH_ORGANIC_MATERIALS</div><div class="optional table-cell">19.96</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/mtng-kelly-platform-ankle-boots-black-mt711n06r-q11.html" class="table-row product-link"><div class="optional table-cell">KELLY - Platform ankle boots - black</div><div class="table-cell">SOCKS</div><div class="optional table-cell">mtng</div><div class="table-cell">CRADLE_TO_CRADLE_GOLD</div><div class="optional table-cell">72.0</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.fr/tamaris-sandales-black-ta111a31f-q11.html" class="table-row product-link"><div class="optional table-cell">Sandales - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Tamaris</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">41.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.amazon.co.uk/Jabra-2393-829-109-2300-Mono-Headset-black/dp/B00H37FJAO/ref=sr_1_23" class="table-row product-link"><div class="optional table-cell">Jabra 2393-829-109 BIZ 2300 USB Mono Headset, Black</div><div class="table-cell">HEADSET</div><div class="optional table-cell">Jabra Store</div><div class="table-cell">TCO</div><div class="optional table-cell">138.0</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.fr/felmini-paros-bottines-cognac-fe211n08v-o11.html" class="table-row product-link"><div class="optional table-cell">PAROS - Bottines - cognac</div><div class="table-cell">SHOES</div><div class="optional table-cell">Felmini</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">113.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/levis-decon-plus-mid-high-top-trainers-light-beige-le211a060-b11.html" class="table-row product-link"><div class="optional table-cell">DECON PLUS MID - High-top trainers - light beige</div><div class="table-cell">SNEAKERS</div><div class="optional table-cell">Levi\'s®</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">74.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.otto.de/p/wat-apparel-print-shirt-flamingo-watercolor-1-tlg-S0B500DA/#variationId=S0B500DA1G1C" class="table-row product-link"><div class="optional table-cell">wat? Apparel Print-Shirt »Flamingo Watercolor« (1-tlg)</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">wat? Apparel</div><div class="table-cell">GOTS_ORGANIC, OTHER</div><div class="optional table-cell">19.9</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/mey-nachtwaesche-hose-light-grey-melange-m9382l02e-c11.html" class="table-row product-link"><div class="optional table-cell">Nachtwäsche Hose - light grey melange</div><div class="table-cell">NIGHTWEAR</div><div class="optional table-cell">mey</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">54.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/marc-opolo-t-shirt-imprime-egg-white-ma322o0hg-a11.html" class="table-row product-link"><div class="optional table-cell">T-shirt imprimé - egg white</div><div class="table-cell">TSHIRT</div><div class="optional table-cell">Marc O\'Polo</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">54.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.co.uk/dr-martens-adrian-unisex-slip-ons-black-smooth-do215c013-q11.html" class="table-row product-link"><div class="optional table-cell">ADRIAN UNISEX - Slip-ons - black smooth</div><div class="table-cell">JACKET</div><div class="optional table-cell">Dr. Martens</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">129.99</div><div class="optional table-cell">GBP</div></a><a href="https://www.zalando.fr/zign-leather-unisex-bottines-a-lacets-black-zi115k00g-q11.html" class="table-row product-link"><div class="optional table-cell">LEATHER UNISEX - Bottines à lacets - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Zign</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">69.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/snocks-snocksgirls-3-pack-string-schwarz-sne81r001-q11.html" class="table-row product-link"><div class="optional table-cell">TANGAS - String - schwarz</div><div class="table-cell">UNDERWEAR</div><div class="optional table-cell">SNOCKS</div><div class="table-cell">GOTS_MADE_WITH_ORGANIC_MATERIALS</div><div class="optional table-cell">24.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.de/anna-field-klassischer-ballerina-black-an611a0nr-q11.html" class="table-row product-link"><div class="optional table-cell">LEATHER BALLERINAS - Klassischer  Ballerina - black</div><div class="table-cell">SHOES</div><div class="optional table-cell">Anna Field</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">40.19</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/armedangels-2-pack-chaussettes-blackwhite-ar381f000-q11.html" class="table-row product-link"><div class="optional table-cell">2 PACK - Chaussettes - black/white</div><div class="table-cell">SOCKS</div><div class="optional table-cell">ARMEDANGELS</div><div class="table-cell">GOTS_MADE_WITH_ORGANIC_MATERIALS</div><div class="optional table-cell">18.99</div><div class="optional table-cell">EUR</div></a></div><div class="table-row"><div class="optional table-header">name</div><div class="table-header">category</div><div class="optional table-header">brand</div><div class="table-header">labels</div><div class="optional table-header">price</div><div class="optional table-header">currency</div></div><a href="https://www.zalando.fr/bugatti-ceinture-noir-bu152d016-q11.html" class="table-row product-link"><div class="optional table-cell">REGULAR - Ceinture - black</div><div class="table-cell">BAG</div><div class="optional table-cell">Bugatti</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">46.95</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/claudie-pierlot-trench-beige-cla21u02h-b11.html" class="table-row product-link"><div class="optional table-cell">GALET - Trench - beige</div><div class="table-cell">JACKET</div><div class="optional table-cell">Claudie Pierlot</div><div class="table-cell">GOTS_ORGANIC</div><div class="optional table-cell">425.0</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/q-s-by-s-oliver-kurzarmshirt-top-mit-spitzenblende-1-tlg-lochstickerei-rueschen-C1585629275/#variationId=S0C4601MF2AC" class="table-row product-link"><div class="optional table-cell">Q/S by s.Oliver Tanktop mit Spitzenblende</div><div class="table-cell">SHIRT</div><div class="optional table-cell">Q/S by s.Oliver</div><div class="table-cell">BIORE, FAIRTRADE_COTTON</div><div class="optional table-cell">11.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.otto.de/p/kangaroos-sweatshirt-in-klassischer-form-1241152480/#variationId=1225780698" class="table-row product-link"><div class="optional table-cell">KangaROOS Sweatshirt in klassischer Form</div><div class="table-cell">SWEATER</div><div class="optional table-cell">KangaROOS</div><div class="table-cell">COTTON_MADE_IN_AFRICA</div><div class="optional table-cell">26.99</div><div class="optional table-cell">EUR</div></a><a href="https://www.zalando.fr/clarks-originals-wallabee-chaussures-a-lacets-rose-pink-cl611n02w-j11.html" class="table-row product-link"><div class="optional table-cell">WALLABEE - Chaussures à lacets - rose pink</div><div class="table-cell">SHOES</div><div class="optional table-cell">Clarks Originals</div><div class="table-cell">LEATHER_WORKING_GROUP</div><div class="optional table-cell">169.95</div><div class="optional table-cell">EUR</div></a></div></div><button class="btn" onclick="\n    event.target.disabled = true;\n    setTimeout(function() {{\n        const stuff = event.target.parentNode.getElementsByClassName(&quot;hidden&quot;)[0];\n        const table = stuff.parentNode;\n        for(var i = 0; i &lt; 4 &amp;&amp; stuff.childNodes.length &gt; 0; i++) {{\n            const k = Math.floor(Math.random() * stuff.childNodes.length);\n            table.appendChild(stuff.childNodes[k]);\n        }}\n        event.target.disabled = stuff.childNodes.length == 0;\n    }}, 400);\n    ">more</button></div>',  # noqa
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
| last updated | **{products_per_country["latest_extraction_timestamp"]}** |
| pages scraped | **{total_scrapes:,}** |
| unique products | **{products_per_cred['all_unique_product_count']:,}** |
| unique credible products | **{products_per_cred['unique_credible_product_count']:,}** |
| product categories | **{len(all_categories)}** |"""
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
    regenerate_color_scheme: bool = True,
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
        tint = [0.1485823416814057, 0.23921176685507542, 0.9116386929265479]
        tint_hover = [blend(a, random(), 0.1) for a in tint]
        tint_hover = [0.15729714510147194, 0.22121801304040017, 0.783397636799458]
        link = [0.3, 0.3, 1]
        link_hover = [blend(medium(random(), 5), a, 0.25) for a in link]
        excerpt = [medium(random(), 12) for i in range(3)]
        excerpt = [0.31466414566023393, 0.08078376977121758, 0.11568391626721704]
        excerpt_hover = [blend(a, medium(random(), 2), 0.2) for a in excerpt]
        excerpt_hover = [0.2730544907353499, 0.13374582147815492, 0.2525970677113762]
        # excerpt_hover = [0.2520087655235149, 0.10649861604954225, 0.09894624196499495]
        more = [blend(a, blend(medium(random(), 80), b, 0.2), 0.4) for a, b in zip(excerpt, tint)]
        more_hover = [blend(a, medium(random(), 20), 0.1) for a in more]
        # more = [0.31466414566023393, 0.08078376977121758, 0.11568391626721704]
        # more_hover = [0.2730544907353499, 0.13374582147815492, 0.2525970677113762]
        # more = [0.13453726110816489, 0.03475241836662604, 0.051237119535906865]
        # more_hover = [0.13904443001423142, 0.039604616161343975, 0.04723897354304182]
        more = [0.8875641033692422, 0.11477726792017197, 0.16015838304306768]
        more_hover = [0.7123934468023223, 0.1067043569269721, 0.16688851531012477]

        more, tint = tint, more
        more_hover, tint_hover = tint_hover, more_hover

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
        link = [0.05469490886457357, 0.01963789069519249, 0.04141276230697474]
        link_hover = [0.06442466199851024, 0.07665787069375272, 0.09772708211693171]
    excerpt = [0.13704307356519763, 0.15924943484172588, 0.5812938149278745]
    excerpt_hover = [0.14373655108035288, 0.12412299681563652, 0.39106001494835]
    link = [0.3, 0.3, 1]
    link_hover = [0.19027607418965353, 0.32350485353551683, 0.7116513755412007]

    # more = [0.31466414566023393, 0.08078376977121758, 0.11568391626721704]
    # more_hover = [0.2520087655235149, 0.10649861604954225, 0.09894624196499495]

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
