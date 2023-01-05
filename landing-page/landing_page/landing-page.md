
:: section#header div.container div.row

# GreenDB: Sustainability Data for Consumer Products

Sebastian Jäger; Felix Bießmann; Alexander Flick; Jessica Adriana Sanchez Garcia; Karl Brendel

:: section div.container div.row
::: column.weight=5

GreenDB is a publicly available database of sustainable products, scraped from European online shops on a weekly basis. As proxy for the products’ sustainability, it relies on sustainability labels, which are evaluated by experts.

The GreenDB schema extends the well-known schema.org Product definition and can be readily integrated into existing product catalogs to improve sustainability information available for search and recommendation experiences.

::: column.weight=3
[Data](https://zenodo.org/record/6576662){.btn}[Publications](#publications){.btn}[Demos](/demo){.btn}[Github](https://github.com/calgo-lab/green-db/){.btn}

:: section#excerpt div.container
## Sample
::: div.row column content.name=excerpt

:: section#schema div.container div.row

## Schema

::: column

### Products

| **name** | **data type** | **nullable** |
| - | -: | -
| timestamp | `timestamp` | no
| url | `text` | no
| source | `text` | no
| merchant | `text` | no
| country | `text` | no
| category | `text` | no
| name | `text` | no
| description | `text` | no
| brand | `text` | no
| sustainability_labels | `array[text]` | no
| price | `numeric` | no
| currency | `text` | no
| image_urls | `array[text]` | no
| gender | `text` | yes
| consumer_lifestage | `text` | yes
| colors | `array[text]` | yes
| sizes | `array[text]` | yes
| gtin | `int` | yes
| asin | `text` | yes


::: column

### Sustainability labels

| **name** | **data type** | **nullable**
| - | -: | -
| id | `text` | no
| timestamp | `timestamp` | no
| name | `text` | no
| description | `text` | no
| cred_credibility | `int4` | yes
| eco_chemicals | `int4` | yes
| eco_lifetime | `int4` | yes
| eco_water | `int4` | yes
| eco_inputs | `int4` | yes
| eco_quality | `int4` | yes
| eco_energy | `int4` | yes
| eco_waste_air | `int4` | yes
| eco_environmental_management | `int4` | yes
| social_labour_rights | `int4` | yes
| social_business_practice | `int4` | yes
| social_social_rights | `int4` | yes
| social_company_responsibility | `int4` | yes
| social_conflict_minerals | `int4` | yes

:: section div.container div.row

::: column.weight=5
Figure 1. Products with credible sustainability labels
:::: content.name=plot_credible_products

::: column.weight=3
Table 1. Brands ranked by aggregated mean sustainability score.
:::: content.name=rank_by_brand_top_25

:: section#publications div.container div.row column

### Publications

* [Jäger, S., Greene, J., Jakob, M., Korenke, R., Santarius, T., and Bießmann, F. (2022). GreenDB: Toward a Product-by-Product Sustainability Database. ArXiv, abs/2205.02908.](https://arxiv.org/abs/2205.02908){.link}
* [Jäger, S., Flick, A., Sanchez Garcia, J. A., von den Driesch, K., Brendel, K., and Bießmann, F. (2022). GreenDB: A Dataset and Benchmark for Extraction of Sustainability Information of Consumer Goods., ArXiv, abs/2207.10733.](https://arxiv.org/abs/2207.10733){.link}

:: footer div.container div.row

.

