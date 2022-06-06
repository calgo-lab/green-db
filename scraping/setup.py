# Automatically created by: scrapyd-deploy

from setuptools import find_packages, setup

setup(
    name="project",
    version="1.0",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = scraping.settings"]},
    package_data={"scraping": ["data/*.json"]},
)
