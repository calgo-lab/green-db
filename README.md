# GreenDB

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6078039.svg)](https://doi.org/10.5281/zenodo.6078039)

This repository contains code and infrastructure components (Helm charts) that powers the Green Database (GreenDB). This development is part of the research project [*Green Consumption Assistant (GCA)*](https://green-consumption-assistant.de).

The publicly available open GreenDB is a product database. It contains classical product attributes, e.g., `name`, `description`, `color`, etc. On the other hand, it also includes information about the products' sustainability. Moreover, this sustainability information is transparently evaluated so that it is possible to rank products depending on their sustainability.
This enables the implementation of applications such as the prototypical Chrome Extension [*Koala - Ecosia Assistant Beta - Grün shoppen*](https://chrome.google.com/webstore/detail/koala-ecosia-assistant-be/anhndceoafjjdihnjnpojdihgboocgpa), which we built as part of the GCA project. The Koala detects when and what users would like to buy online and offers more sustainable alternatives. More information can be found in [one of our working papers [1]](https://green-consumption-assistant.de/wp-content/uploads/GCA-Working-Paper-I-Scaling-Sustainability-Advice.pdf).

With the open GreenDB, we hope to contribute to the fight against climate change by enabling others to build applications that support more sustainable consumption. Further, we plan to publish datasets to support the research community.

If you would like to participate with code, data, or anything else, [reach out to use!](#contact)


## Where do we get product and sustainability information?

Nowadays, some online shops offer `sustainability` filters. We use scraping technologies to automatically find these sustainable products and integrate them into the GreenDB. Further, we evaluate the sustainability information and (currently) use easily accessible scores (0 - 100) for three sustainability dimensions: `social`, `ecological`, and their `credibility`.

However, manual evaluating products does not scale well. Therefore, we leverage that products can be certified with *sustainability labels*. The German website [Siegelklarheit](https://www.siegelklarheit.de) systematically evaluates sustainability labels and makes their results publicly available. We use these  to infer a products' sustainability if it is certified with a sustainability label.


## GreenDB schema

The GreenDB schema is highly inspired by [schema.org](https://schema.org). However, this is still a proof of concept implementation and can differ from their definitions (e.g., the `brand` column of the [`green-db` table](#table-green-db)). One of our future plans is to tackle this and make the GreenDB fully compatible with [schema.org's Product](https://schema.org/Product) definition. Our ultimate goal is to eventually contribute an extension of schema.org that integrates the products' sustainability information.


### Table: `green-db`

| **column name**      | **id** | **gtin** | **asin** | **timestamp** | **url** | **merchant** | **category** | **name** | **description** | **brand** | **sustainability_labels** | **price** | **currency** | **image_urls** | **color** | **size** |
| -------------------- | ------ | -------- | -------- | ------------- | ------- | ------------ | ------------ | -------- | --------------- | --------- | ------------------------- | --------- | ------------ | -------------- | --------- | -------- |
| **column data type** | int4   | int8     | text     | timestamp     | text    | text         | text         | text     | text            | text      | array[text]               | numeric   | text         | array[text]    | text      | text     |
| **column nullable**  | no     | yes      | yes      | no            | no      | no           | no           | no       | no              | no        | no                        | no        | no           | no             | yes       | yes      |


**Please note**: Currently, we use our own `category` strings, which are not documented. However, we plan to switch to [Google's product category](https://support.google.com/merchants/answer/6324436?hl=en) to rely on a public definition of the `category` column.


### Table: `sustainability-labels`

| **column name**      | **id** | **timestamp** | **name** | **description** | **ecological_evaluation** | **social_evaluation** | **credibility_evaluation** |
| -------------------- | ------ | ------------- | -------- | --------------- | ------------------------- | --------------------- | -------------------------- |
| **column data type** | text   | timestamp     | text     | text            | int4                      | int4                  | int4                       |
| **column nullable?** | no     | no            | no       | no              | yes                       | yes                   | yes                        |


## Future plans

- [x] We are already working on a first publication of the GreenDB dataset.

- [ ] In the near future, we plan to extend the GreenDB to more shops and non-German markets. We hope to drastically increase its product and sustainability label coverage and make it, therefore, more interesting to a wider range of potential users.

- [ ] As mentioned above, we plan to switch to a publicly available product taxonomy to replace the `category` column. Further, we work on minor refactorings to be fully compatible to schema.org.


## Contact

- Main developer of the GreenDB: sebastian.jaeger@bht-berlin.de
- Green Consumption Assistant research project: https://green-consumption-assistant.de/kontakt/ 


## Research

- [1]: Cathérine Lehmann. (2021). Scaling sustainability advice - Options for generating large-scale green consumption recommendations. URL: https://green-consumption-assistant.de/wp-content/uploads/GCA-Working-Paper-I-Scaling-Sustainability-Advice.pdf



## Disclaimer!

This is research code and under development and not supposed to be used in production.