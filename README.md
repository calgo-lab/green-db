# GreenDB


**Preprint:** [![arXiv](https://img.shields.io/badge/arXiv-2205.02908-blue)](https://arxiv.org/abs/2205.02908)\
**Dataset:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6078038.svg)](https://doi.org/10.5281/zenodo.6078038)



This repository contains code and infrastructure components (Helm charts) that powers the Green Database (GreenDB). This development is part of the research project [*Green Consumption Assistant (GCA)*](https://green-consumption-assistant.de).

The publicly available open GreenDB is a product database. It contains classical product attributes, e.g., `name`, `description`, `colors`, etc. On the other hand, it also includes information about the products' sustainability. Moreover, this sustainability information is transparently evaluated so that it is possible to rank products depending on their sustainability. For more information about the GreenDB dataset or technical details see [the dataset on zenodo [1]](https://doi.org/10.5281/zenodo.6078038) or [our preprint on arXiv [2]](https://arxiv.org/abs/2205.02908).

The GreenDB enables the implementation of applications such as the prototypical Chrome Extension [*Koala - Ecosia Assistant Beta - Grün shoppen*](https://chrome.google.com/webstore/detail/koala-ecosia-assistant-be/anhndceoafjjdihnjnpojdihgboocgpa), which we built as part of the GCA project. The Koala detects when and what users would like to buy online and offers more sustainable alternatives. More information can be found in [one of our working papers [3]](https://green-consumption-assistant.de/wp-content/uploads/GCA-Working-Paper-I-Scaling-Sustainability-Advice.pdf).

With the open GreenDB, we hope to contribute to the fight against climate crises by enabling others to build applications that support more sustainable consumption. Further, we plan to publish datasets to support the research community.

If you would like to participate with code, data, or anything else, [reach out to use!](#contact)


## Where do we get product and sustainability information?

Nowadays, some online shops offer `sustainability` filters. We use scraping technologies to automatically find these sustainable products and integrate them into the GreenDB. Further, we evaluate the sustainability information and use easily accessible scores (0 - 100) for fine-grained aspects of three sustainability dimensions: `social`, `ecological`, and their `credibility`.

However, manual evaluating products does not scale well. Therefore, we leverage that products can be certified with *sustainability labels*. The German website [Siegelklarheit](https://www.siegelklarheit.de) systematically evaluates sustainability labels and makes their results publicly available. We use these to infer a products' sustainability if it is certified with a sustainability label.


## GreenDB schema

The GreenDB schema is highly inspired by [schema.org](https://schema.org). However, this is still a proof of concept implementation and can differ from their definitions (e.g., the `brand` column of the [`green-db` table](#table-green-db)). One of our future plans is to tackle this and make the GreenDB fully compatible with [schema.org's Product](https://schema.org/Product) definition. Our ultimate goal is to eventually contribute an extension of schema.org that integrates the products' sustainability information.


### Table: `green-db`

| **column name**      | **id** | **gtin** | **asin** | **timestamp** | **url** | **source** | **merchant** | **country** | **category** | **name** | **description** | **brand** | **sustainability_labels** | **price** | **currency** | **image_urls** | **colors**  | **sizes**   | **gender** | **consumer_lifestage** |
| -------------------- | ------ | -------- | -------- | ------------- | ------- | ---------- | ------------ | ----------- | ------------ | -------- | --------------- | --------- | ------------------------- | --------- | ------------ | -------------- | ----------- | ----------- | ---------- | ---------------------- |
| **column data type** | int4   | int8     | text     | timestamp     | text    | text       | text         | text        | text         | text     | text            | text      | array[text]               | numeric   | text         | array[text]    | array[text] | array[text] | text       | text                   |
| **column nullable**  | no     | yes      | yes      | no            | no      | no         | no           | no          | no           | no       | no              | no        | no                        | no        | no           | no             | yes         | yes         | yes        | yes                    |


**Please note**: Currently, we use our own `category` strings, which are not documented. However, we plan to switch to the [GS1 Global Product Classification](https://www.gs1.org/standards/gpc) taxonomy to rely on a public definition of the `category` column.


### Table: `sustainability-labels`

| **column name**      | **id** | **timestamp** | **name** | **description** | **cred_credibility** | **eco_chemicals** | **eco_lifetime** | **eco_water** | **eco_inputs** | **eco_quality** | **eco_energy** | **eco_waste_air** | **eco_environmental_management** | **social_labour_rights** | **social_business_practice** | **social_social_rights** | **social_company_responsibility** |
| -------------------- | ------ | ------------- | -------- | --------------- | -------------------- | ----------------- | ---------------- | ------------- | -------------- | --------------- | -------------- | ----------------- | -------------------------------- | ------------------------ | ---------------------------- | ------------------------ | --------------------------------- |
| **column data type** | text   | timestamp     | text     | text            | int4                 | int4              | int4             | int4          | int4           | int4            | int4           | int4              | int4                             | int4                     | int4                         | int4                     | int4                              |
| **column nullable?** | no     | no            | no       | no              | yes                  | yes               | yes              | yes           | yes            | yes             | yes            | yes               | yes                              | yes                      | yes                          | yes                      | yes                               |


## Cite us

If you are using our code or the GreenDB dataset, please reference the [preprint](https://arxiv.org/abs/2205.02908) as:
```
@misc{https://doi.org/10.48550/arxiv.2205.02908,
  doi = {10.48550/ARXIV.2205.02908},
  url = {https://arxiv.org/abs/2205.02908},
  author = {Jäger, Sebastian and Greene, Jessica and Jakob, Max and Korenke, Ruben and Santarius, Tilman and Biessmann, Felix},
  keywords = {Machine Learning (cs.LG), FOS: Computer and information sciences, FOS: Computer and information sciences},
  title = {GreenDB: Toward a Product-by-Product Sustainability Database},
  publisher = {arXiv},
  year = {2022}
}
```



## Future plans

- [x] We are already working on a first publication of the GreenDB dataset.

- [x] In the near future, we plan to extend the GreenDB to more shops and non-German markets. We hope to drastically increase its product and sustainability label coverage and make it, therefore, more interesting to a wider range of potential users.

- [ ] As mentioned above, we plan to switch to the [GS1 Global Product Classification](https://www.gs1.org/standards/gpc) taxonomy to replace the `category` column. Further, we work on minor refactorings to be fully compatible to schema.org.


## Contact

- Main developer of the GreenDB: sebastian.jaeger@bht-berlin.de
- Green Consumption Assistant research project: https://green-consumption-assistant.de/kontakt/ 


## Research

- [1]: Jäger, Sebastian, Bießmann, Felix, Flick, Alexander, Sanchez Garcia, Jessica Adriana, von den Driesch, Kaspar, & Brendel, Karl. (2022). GreenDB: A Product-by-Product Sustainability Database [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6078038
- [2]: Jäger, S., Greene, J., Jakob, M., Korenke, R., Santarius, T., & Biessmann, F. (2022). GreenDB: Toward a Product-by-Product Sustainability Database. [ArXiv, abs/2205.02908](https://arxiv.org/abs/2205.02908).
- [3]: Cathérine Lehmann. (2021). Scaling sustainability advice - Options for generating large-scale green consumption recommendations. URL: https://green-consumption-assistant.de/wp-content/uploads/GCA-Working-Paper-I-Scaling-Sustainability-Advice.pdf


## Publications that use the GreenDB

1. Gossen, M., Jäger, S., Hoffmann, M.L., Biessmann, F., Korenke, R., & Santarius, T. (2022). Nudging Sustainable Consumption: A Large-Scale Data Analysis of Sustainability Labels for Fashion in German Online Retail. Frontiers in Sustainability. DOI: https://doi.org/10.3389/frsus.2022.922984 
2. Jäger, S., Flick, A., Garcia, J.A., Driesch, K.V., Brendel, K., & Biessmann, F. (2022). GreenDB - A Dataset and Benchmark for Extraction of Sustainability Information of Consumer Goods. [ArXiv, abs/2207.10733](https://arxiv.org/abs/2207.10733). DOI: https://doi.org/10.48550/arXiv.2207.10733
3. Flick, A., Jäger, S., Trajanovska, I., Biessmann, F. (2023). Automated Extraction of Fine-Grained Standardized Product Information from Unstructured Multilingual Web Data. In: , et al. Advances in Information Retrieval. ECIR 2023. Lecture Notes in Computer Science, vol 13982. Springer, Cham. https://doi.org/10.1007/978-3-031-28241-6_19

## Disclaimer!

This is research code and under development and not supposed to be used in production.
