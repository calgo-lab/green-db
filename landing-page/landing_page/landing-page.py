from random import random
from typing import Any, Dict, List, Optional

import plotly.express as px
from minify_html import minify
from plotly.io import to_html
from plotly.offline import get_plotlyjs
from utils import Element, render_markdown, render_page

from database.connection import GreenDB


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


def map(func: Any, *iterables: Any, **kwargs: Any) -> Any:
    return (func(*args, **kwargs) for args in zip(*iterables))


def webcolor(color: List[float]) -> str:
    return "#" + "".join(f"{int(to_srgb(c)*255):02x}" for c in color)


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


regenerate_color_scheme = False

if regenerate_color_scheme:
    tint = [medium(random(), 8) for i in range(3)]
    tint_hover = [blend(a, medium(random(), 20), 0.1) for a in tint]
    link = [medium(random(), 50) for a in range(3)]
    link_hover = [blend(medium(random(), 12), a, 0.25) for a in link]
    print("tint =", tint)
    print("tint_hover =", tint_hover)
    print("link =", link)
    print("link_hover =", link_hover)
else:
    tint = [0.8875641033692422, 0.11477726792017197, 0.16015838304306768]
    tint_hover = [0.7123934468023223, 0.1067043569269721, 0.16688851531012477]
    link = [0.05469490886457357, 0.01963789069519249, 0.04141276230697474]
    link_hover = [0.06442466199851024, 0.07665787069375272, 0.09772708211693171]

foot = [blend(a, 0.02, 0.92) for a in tint_hover]
white = [1, 1, 1]


def build_test_content() -> Dict[str, str]:
    certs = "BETTER_COTTON_INITIATIVE BIORE BLUESIGN_APPROVED BLUESIGN_PRODUCT COTTON_MADE_IN_AFRICA CRADLE_TO_CRADLE_BRONZE CRADLE_TO_CRADLE_GOLD CRADLE_TO_CRADLE_SILVER".split()  # noqa
    table = "\n".join(f"|{i}|{cert}|{len(cert)}" for i, cert in enumerate(certs))
    table = render_markdown(f"|index|name|idk\n|-|-|-\n{table}")

    df = GreenDB().get_product_count_by_sustainability_label_credibility()
    pie = px.pie(df[df.type == "credible"], values="product_count", names="merchant")

    return {"table1": table, "graph1": render_plotly_figure(pie)}


def rebuild_landing_page(
    content_map: Optional[Dict[str, str]] = None,
    page_title: str = "GreenDB",
    description: str = "A Product-by-Product Sustainability Database",
    page_url: str = "https://calgo-lab.github.io/greendb",
    image_url: str = "https://calgo-lab.github.io/greendb/greendb.jpg",
    image_alt_text: str = "GreenDB",
) -> str:
    """builds the"""

    content = build_test_content() if content_map is None else content_map

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
            if parent.children and isinstance(parent.children[-1], Column):
                self.row = parent.children[-1].add_column(self)

        def on_close_parent(self) -> Any:
            self.html_tag = "div"
            self.css_class.append("col")
            if self.row is not None:
                total_weight = sum(col.weight for col in self.row)
                self.css_class.append(width_class(self.weight / total_weight))

    element_map = {"column": Column, "content": Content}
    with open("landing-page.md", "r", encoding="utf-8") as file:
        body = render_page(file.read(), element_map)

    return minify(
        f"""<!DOCTYPE html>
<html lang="en" class="no-js">
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

.col {{
    padding: 0 25px;
}}

.container {{
    margin-right: auto;
    margin-left: auto;
}}

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


* {{ box-sizing: border-box }}

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
    padding: 30px 0;
}}

footer {{
    padding: 40px 0px;
    text-align: center;
    background: {webcolor(foot)};
    color: white;
}}

.link {{
    color: {webcolor(link)}
}}

.link:hover {{
    color: {webcolor(link_hover)}
}}

.btn {{
    margin: 7px;
    border-radius: 4.3px;
    padding: 15px;
    font-size: 1.25em;
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

table {{
    width: 100%;
    max-width: 100%;
    line-height: 1.2;
    margin-bottom: 20px;
    background-color: transparent;
    border-spacing: 0;
    border-collapse: collapse;
}}

th {{ text-align:left }}
th,
td {{ padding: 8px }}

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
    with open("landing-page.html", "w", encoding="utf-8") as f:
        f.write(content)
