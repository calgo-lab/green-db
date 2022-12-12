import re
from typing import List
from random import random
from ast import literal_eval 
from typing import NamedTuple
from markdown_it import MarkdownIt
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.container import container_plugin

md = MarkdownIt().enable('table').use(attrs_plugin)
for i in range(10):
	md = md.use(container_plugin, name=f'col{i}')


def to_linear(srgb: float):
	if srgb < 0: return 0
	if srgb > 1: return 1
	if srgb < .04045: return srgb / 12.92
	return pow((srgb + .055) / 1.055, 2.4)


def to_srgb(linear: float):
	if linear < 0: return 0
	if linear > 1: return 1
	if linear < .0031308: return linear * 12.92
	return pow(linear, 1./2.4) * 1.055 - .055


def shadow(bg: float, fg: float, s=.5, p=.62):
	return bg * s / (1. - p * bg * fg)


def medium(a: float, t: float):
	return 1 / (t*(1 - a) + 1)


def blend(a: float, b: float, t: float):
	return (1 - t)**2 * a / (1 - t * a * b) + t * b


def map(func, *iterables, **kwargs):
	return (func(*args, **kwargs) for args in zip(*iterables))


def webcolor(color: List[float]):
	return '#' + "".join(f'{int(to_srgb(c)*255):02x}' for c in color)


def make_green(color: List[float]):
	color = sorted(color)
	color[1], color[2] = color[2], color[1]
	return color


def section(markdown, name=None, tag='section'):
	pre = f'<{tag}><div class="container"><div class="row">'
	post = f'</div></div></{tag}>'
	if name:
		pre = f'<{tag} id="{name}"><div class="container"><div class="row">'
	return f'{pre}{md.render(markdown)}{post}'


regenerate_color_scheme = False

page_title = 'GreenDB'
page_description = 'A Product-by-Product Sustainability Database'
image_alt_text = 'GreenDB'

page_url = 'https://calgo-lab.github.io/greendb'
image_url = 'https://calgo-lab.github.io/greendb/greendb.jpg'

newline = '\n'

certs = 'BETTER_COTTON_INITIATIVE BIORE BLUESIGN_APPROVED BLUESIGN_PRODUCT COTTON_MADE_IN_AFRICA CRADLE_TO_CRADLE_BRONZE CRADLE_TO_CRADLE_GOLD CRADLE_TO_CRADLE_SILVER'.split()

sections = []

sections.append(section(f'''

# GreenDB: A Product-by-Product Sustainability Database

Sebastian Jäger; Felix Bießmann; Alexander Flick; Jessica Adriana Sanchez Garcia; Karl Brendel

''', name='header'))

sections.append(section(f'''

::: col2

The production, shipping, usage, and disposal of consumer goods have a substantial impact on greenhouse gas emissions and the depletion of resources. Machine Learning (ML) can help to foster sustainable consumption patterns by accounting for sustainability aspects in product search or recommendations of modern retail platforms. However, the lack of large high quality publicly available product data with trustworthy sustainability information impedes the development of ML technology that can help to reach our sustainability goals.

Here we present GreenDB, a database that collects products from European online shops on a weekly basis. As proxy for the products’ sustainability, it relies on sustainability labels, which are evaluated by experts. The GreenDB schema extends the well-known schema.org Product definition and can be readily integrated into existing product catalogs. We present initial results demonstrating that ML models trained with our data can reliably predict the sustainability label of products. These contributions can help to complement existing e-commerce experiences and ultimately encourage users to more sustainable consumption patterns.

:::

::: col3

| index | name | idk\n|-|-|-
{newline.join(f"| {i} | {cert} | {len(cert)}" for i,cert in enumerate(certs))}


:::

'''))



sections.append(section('''

::: col3

[Read the Paper](https://arxiv.org/abs/2205.02908){.btn}[Demos](/demo){.btn}[Zenodo](https://zenodo.org/record/6576662){.btn}[Github](https://github.com/calgo-lab/green-db/){.btn}

:::

::: col2

Modern retail platforms rely heavily on
Machine Learning (ML) for their search and recommender systems.
Thus, ML can potentially support efforts towards more sustainable
consumption patterns, for example, by accounting for sustainability
aspects in product search or recommendations. However, leveraging
ML potential for reaching sustainability goals requires data on sustainability. Unfortunately, no open and publicly available database
integrates sustainability information on a product-by-product basis.
In this work, we present the GreenDB, which fills this gap. Based on
search logs of millions of users, we prioritize which products users
care about most. The GreenDB schema extends the well-known
schema.org Product definition and can be readily integrated into
existing product catalogs to improve sustainability information
available for search and recommendation experiences. We present
our proof of concept implementation of a scraping system that
creates the GreenDB dataset.

:::

'''))

sections.append(section('''

::: col1

### Publications

* [Jäger, S., Greene, J., Jakob, M., Korenke, R., Santarius, T., and Bießmann, F. (2022). GreenDB: Toward a Product-by-Product Sustainability Database. ArXiv, abs/2205.02908.](https://arxiv.org/abs/2205.02908){.citation}
* [Jäger, S., Flick, A., Sanchez Garcia, J. A., von den Driesch, K., Brendel, K., and Bießmann, F. (2022). GreenDB: A Dataset and Benchmark for Extraction of Sustainability Information of Consumer Goods., ArXiv, abs/2207.10733.](https://arxiv.org/abs/2207.10733){.citation}

:::

'''))

sections.append(section('''

::: col4

.

:::

''', tag='footer'))






white = [1, 1, 1]

if regenerate_color_scheme:
	tint = make_green(medium(random(), 8) for i in range(3))
	tint_hover = [blend(a, medium(random(), 20), .1) for a in tint]
	link = [medium(random(), 50) for a in range(3)]
	link_hover = [blend(medium(random(), 12), a, .25) for a in link]
	print('tint =', tint)
	print('tint_hover =', tint_hover)
	print('link =', link)
	print('link_hover =', link_hover)
	print('foot =', foot)
else:
	tint = [0.8875641033692422, 0.11477726792017197, 0.16015838304306768]
	tint_hover = [0.7123934468023223, 0.1067043569269721, 0.16688851531012477]
	link = [0.05469490886457357, 0.01963789069519249, 0.04141276230697474]
	link_hover = [0.06442466199851024, 0.07665787069375272, 0.09772708211693171]


foot = [blend(a, .02, .94) for a in tint]


with open('landing-page.html', "w", encoding="utf-8") as f:
	f.write(f'''
<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<script type="module">
document.documentElement.classList.remove('no-js');
document.documentElement.classList.add('js');
</script>
<style>

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

.container {{
	margin-right: auto;
	margin-left: auto;
}}

.row::before,
.row::after {{
	display: table;
	content: "";
}}

.row::after {{
	clear: both;
}}

.col1,
.col2,
.col3,
.col4 {{
	padding: 0 25px;
}}

@media (min-width:768px) {{
	.container {{ width:750px }}
}}

@media (min-width:992px) {{
	.container {{ width:970px }}
	.col2,
	.col3 {{ float: left }}
	.col2 {{ width: 62% }}
	.col3 {{ width: 38% }}
}}

@media (min-width:1200px) {{
	.container {{ width:1170px }}
}}

.citation {{
	color: {webcolor(link)}
}}

.citation:hover {{
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
<meta name="description" content="{page_description}">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{page_description}">
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
<body>
{''.join(sections)}
</body>
</html>
''')

# https://www.matuzo.at/blog/html-boilerplate/
# <meta name="theme-color" content="{webcolor(tint)}">
# <link rel="stylesheet" href="/assets/css/styles.css">
# <link rel="stylesheet" href="/assets/css/print.css" media="print">
# <link rel="apple-touch-icon" href="/apple-touch-icon.png">
# <link rel="manifest" href="/my.webmanifest">


# publications
# zenodo
# github
# project page
# demos