
:: section#header div.container div.row

# GreenDB: A Product-by-Product Sustainability Database

Sebastian Jäger; Felix Bießmann; Alexander Flick; Jessica Adriana Sanchez Garcia; Karl Brendel

:: section div.container div.row
::: column.weight=5

The production, shipping, usage, and disposal of consumer goods have a substantial impact on greenhouse gas emissions and the depletion of resources. Machine Learning (ML) can help to foster sustainable consumption patterns by accounting for sustainability aspects in product search or recommendations of modern retail platforms. However, the lack of large high quality publicly available product data with trustworthy sustainability information impedes the development of ML technology that can help to reach our sustainability goals.

Here we present GreenDB, a database that collects products from European online shops on a weekly basis. As proxy for the products’ sustainability, it relies on sustainability labels, which are evaluated by experts. The GreenDB schema extends the well-known schema.org Product definition and can be readily integrated into existing product catalogs. We present initial results demonstrating that ML models trained with our data can reliably predict the sustainability label of products. These contributions can help to complement existing e-commerce experiences and ultimately encourage users to more sustainable consumption patterns.

::: column.weight=3 content.name=table1

:: section div.container div.row
::: column.weight=3

[Read the Paper](https://arxiv.org/abs/2205.02908){.btn}[Demos](/demo){.btn}[Zenodo](https://zenodo.org/record/6576662){.btn}[Github](https://github.com/calgo-lab/green-db/){.btn}

::: column.weight=5

Modern retail platforms rely heavily on Machine Learning (ML) for their search and recommender systems. Thus, ML can potentially support efforts towards more sustainable consumption patterns, for example, by accounting for sustainability aspects in product search or recommendations. However, leveraging ML potential for reaching sustainability goals requires data on sustainability. Unfortunately, no open and publicly available database integrates sustainability information on a product-by-product basis. In this work, we present the GreenDB, which fills this gap. Based on search logs of millions of users, we prioritize which products users care about most. The GreenDB schema extends the well-known schema.org Product definition and can be readily integrated into existing product catalogs to improve sustainability information available for search and recommendation experiences. We present our proof of concept implementation of a scraping system that creates the GreenDB dataset.

:: section#publications div.container div.row column

### Publications

* [Jäger, S., Greene, J., Jakob, M., Korenke, R., Santarius, T., and Bießmann, F. (2022). GreenDB: Toward a Product-by-Product Sustainability Database. ArXiv, abs/2205.02908.](https://arxiv.org/abs/2205.02908){.link}
* [Jäger, S., Flick, A., Sanchez Garcia, J. A., von den Driesch, K., Brendel, K., and Bießmann, F. (2022). GreenDB: A Dataset and Benchmark for Extraction of Sustainability Information of Consumer Goods., ArXiv, abs/2207.10733.](https://arxiv.org/abs/2207.10733){.link}

:: footer div.container div.row

.

