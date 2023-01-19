
:: section#header div.container div.row

# GreenDB: Sustainability Data for Consumer Products

:: section div.container

::: div.row
:::: column.weight=5

GreenDB is a publicly available database of sustainable products, scraped from European online shops on a weekly basis. As proxy for the products’ sustainability, it relies on sustainability labels, which are evaluated by experts. The GreenDB schema extends the well-known schema.org Product definition and can be readily integrated into existing product catalogs to improve sustainability information available for search and recommendation experiences.

:::: column.weight=3 div.stats content.name=stats

::: div.row div.ff

[Data](https://doi.org/10.5281/zenodo.6078038){.btn}[Publications](#publications){.btn}[Demos](#demos){.btn}[Github](https://github.com/calgo-lab/green-db/){.btn}

:: section div.container div.row
## Sample
::: div.ff content.name=excerpt

:: section div.container
## Schema

### Products

::: div.row div.ff div.table-wrapper
| **column name** | timestamp | url | source | merchant | country | category | name | description | brand | sustainability_labels | price | currency | image_urls | gender | consumer_lifestage | colors | sizes | gtin | asin
| -: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-:
| **data type** | timestamp | text | text | text | text | text | text | text | text | array[text] | numeric | text | array[text] | text | text | array[text] | array[text] | int | text
| **nullable** | no | no | no | no | no | no | no | no | no | no | no | no | no | yes | yes | yes | yes | yes | yes
:::

### Sustainability labels

::: div.row div.ff div.table-wrapper
| **column name** | id | timestamp | name | description | cred_credibility | eco_chemicals | eco_lifetime | eco_water | eco_inputs | eco_quality | eco_energy | eco_waste_air | eco_environmental_management | social_labour_rights | social_business_practice | social_social_rights | social_company_responsibility | social_conflict_minerals
| -: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-:
| **data type** | text | timestamp | text | text | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4 | int4
| **nullable** | no | no | no | no | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes

:: section div.container div.row
::: content.name=plot_category_cred

:: section#demos div.container

## Demos

::: div.row div.ff
* [Automated extraction of product information](https://product-classification.demo.calgo-lab.de/){.link}

:: section#publications div.container

## Publications

::: div.row div.ff

* [Jäger, S., Greene, J., Jakob, M., Korenke, R., Santarius, T., and Bießmann, F. (2022). GreenDB: Toward a Product-by-Product Sustainability Database. ArXiv, abs/2205.02908.](https://arxiv.org/abs/2205.02908){.link}
* [Jäger, S., Flick, A., Sanchez Garcia, J. A., von den Driesch, K., Brendel, K., and Bießmann, F. (2022). GreenDB: A Dataset and Benchmark for Extraction of Sustainability Information of Consumer Goods., ArXiv, abs/2207.10733.](https://arxiv.org/abs/2207.10733){.link}

:: footer div.container div.row

.

