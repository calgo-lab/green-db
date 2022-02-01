# `workers` Package

The `workers` package:
- implements workers for each of the currently used queues:
  - [`scraping`](./workers/scraping.py): Simply writes the given `ScrapedPage`s into the scraping table.
  - [`extract`](./workers/extract.py): Parses the `ScrapedPage`'s HTML and extracts product attributes and sustainability information and inserts the `Product` into the GreenDB.
- implements an CLI to start the workers that listen on the above queues, [see here.](./workers/main.py)

This directory also contains a [`Dockerfile`](./Dockerfile) used to build a `workers` image.