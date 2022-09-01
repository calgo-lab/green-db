from typing import TypeAlias

import numpy as np
import pandas as pd
import plotly.express as px

from database.connection import GreenDB
from monitoring import CONNECTION_FOR_TABLE

DataFrame: TypeAlias = pd.DataFrame
green_db = GreenDB()


def dates() -> tuple:
    """
    Gets latest timestamp for green-db and sustainability-labels tables and converts it to date
    format.

    Returns:
        Tuple: with date of last extraction from green-db and date of last update from
        sustainability-labels
    """
    last_extraction = green_db.get_latest_timestamp().date()
    last_label_update = green_db.get_latest_timestamp(SustainabilityLabelsTable).date()
    return last_extraction, last_label_update


def latest_extraction_summary() -> tuple:
    """
    Uses 'get_latest_extraction_summary' to fetch number of extracted products for latest available
    timestamp by merchant. Counts number of merchants.

    Returns:
        Tuple: with objects to display in the monitoring app.
    """
    df = green_db.get_latest_extraction_summary()
    number_products = df["products"].sum()
    number_merchants = len(df.groupby("merchant"))
    return df, number_products, number_merchants


def latest_scraping_summary() -> tuple:
    """
    Uses 'get_latest_scraping_summary' to fetch number of scraped products for latest available
    timestamp by merchant, query all tables in ScrapingDB and concatenates the result in a
    DataFrame.

    Returns:
        Tuple: with objects to display in the monitoring app.
    """
    all_scraping = []
    for value in CONNECTION_FOR_TABLE.values():
        all_scraping.extend(value.get_latest_scraping_summary())
    df = pd.DataFrame(
        all_scraping, columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")
    number_products = df["products"].sum()
    return df, number_products


def products_by_category() -> tuple:
    """
    Uses 'get_latest_category_summary' output to create a bar chart for products per category
    and a pivot table. Counts number of categories.

    Returns:
        Tuple: with objects to display in the monitoring app.
    """
    df = green_db.get_latest_category_summary()
    df_products_by_category = df.pivot_table(
        values="products", index=["category"], columns="merchant", fill_value=0
    )
    fig_products_by_category = px.bar(
        df, x="category", y="products", color="merchant", text="products"
    )
    number_cat = len(df.groupby("category"))
    return fig_products_by_category, df_products_by_category, number_cat


def all_timestamps() -> tuple:
    """
    Concatenates 'all_extraction_summary' and 'all_scraping_summary' Dataframes to create:
    1) Line chart and DataFrame for extracted and scraped products for all timestamps found by
    merchant. A second DataFrame including country level.
    2) Line chart and DataFrame for extracted and scraped products for all timestamps

    Returns:
        Tuple: with objects to display in the monitoring app.
    """
    extraction = green_db.get_extraction_summary()
    extraction["type"] = "extraction"
    all_scraping = []
    for value in CONNECTION_FOR_TABLE.values():
        all_scraping.extend(value.get_scraping_summary())
    scraping = pd.DataFrame(
        all_scraping, columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")
    scraping["type"] = "scraping"
    all_timestamps = pd.concat([extraction, scraping], ignore_index=True)
    all_timestamps["date"] = pd.to_datetime(all_timestamps["timestamp"]).dt.date
    df_timestamps_by_merchant = (
        all_timestamps.groupby(by=["date", "merchant", "type"])
        .sum()
        .pivot_table(
            values="products",
            index=["date", "merchant"],
            columns="type",
            aggfunc=np.sum,
            fill_value=0,
        )
        .sort_values(by="date", ascending=False)
    )
    df_timestamps_by_merchant_country = (
        all_timestamps.groupby(by=["date", "merchant", "country", "type"])
        .sum()
        .pivot_table(
            values="products",
            index=["date", "merchant", "country"],
            columns="type",
            aggfunc=np.sum,
            fill_value=0,
        )
        .sort_values(by="date", ascending=False)
    )
    df = all_timestamps.groupby(by=["date", "merchant", "type"]).sum().reset_index()
    fig_timestamps_by_merchant = px.line(
        df, x="date", y="products", color="merchant", symbol="type"
    )
    df_agg = all_timestamps.groupby(by=["date", "type"]).sum().reset_index()
    df_timestamps_agg = df_agg.pivot_table(
        values="products", index=["date"], columns="type", aggfunc=np.sum, fill_value=0
    ).sort_values(by="date", ascending=False)
    fig_timestamps_agg = px.line(df_agg, x="date", y="products", color="type")
    return (
        fig_timestamps_by_merchant,
        df_timestamps_by_merchant,
        df_timestamps_by_merchant_country,
        fig_timestamps_agg,
        df_timestamps_agg,
    )


def products_by_label() -> DataFrame:
    """
    Returns:
        DataFrame: contains products by sustainability label for latest available timestamp.
    """
    return green_db.get_latest_products_by_label()


def labels_known_vs_unknown() -> tuple:
    """
    Gets 'get_labels_known_vs_unknown' from green-db table and creates a line chart to compare
    number of products with 'certificate:UNKNOWN' against product with "Known certificates".

    Returns:
        Tuple: with objects to display in the monitoring app.
    """
    query = green_db.get_labels_known_vs_unknown()
    query["date"] = pd.to_datetime(query["timestamp"]).dt.date
    query_agg = query.groupby(["date", "label"]).sum().reset_index()
    fig_label_unknown = px.line(query_agg, x="date", y="count", color="label")
    df_label_unknown = query_agg.pivot_table(
        values="count", index=["date"], columns="label", aggfunc=np.sum, fill_value=0
    ).sort_values(by="date", ascending=False)
    return (fig_label_unknown, df_label_unknown, green_db.get_latest_products_certificate_unknown())
