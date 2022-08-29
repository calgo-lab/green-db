from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.connection import GreenDB
from monitoring import CONNECTION_FOR_TABLE

green_db = GreenDB()


def dates() -> tuple:
    """
    Gets latest timestamp for green-db and sustainability-labels tables and converts it to date
    format.

    Returns:
        List: containing date of last extraction from green-db and date of last update from
        sustainability-labels
    """
    last_extraction = green_db.get_latest_timestamp().date()
    last_label_update = green_db.last_update_sustainability_labels().date()
    return last_extraction, last_label_update


def all_scraping_summary() -> Any:
    """
    Uses 'get_scraping_summary' method to query all ScrapingDB tables.

    Returns:
        Dataframe: with number of products by country and merchant for all timestamps for all
        existing tables in ScrapingDB
    """
    all_scraping = []
    for value in CONNECTION_FOR_TABLE.values():
        all_scraping.extend(value.get_scraping_summary())
    return pd.DataFrame(
        all_scraping, columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")


def last_scraping_summary() -> Any:
    """
    Filters returned dataframe from 'all_scraping_summary' by latest timestamp found in green-db
    table.

    Returns:
        Dataframe: with number of products by country and merchant for latest timestamp for all
        existing tables in ScrapingDB
    """
    return all_scraping_summary()[
        (all_scraping_summary()["timestamp"] >= green_db.get_latest_timestamp())
    ]


def all_extraction_summary() -> Any:
    """
    Uses 'get_extraction_summary' output and converts it in a dataframe.

    Returns:
        Dataframe: with number of products by country and merchant for all timestamps in green-db
        table.
    """
    return pd.DataFrame(
        green_db.get_extraction_summary(), columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")


def last_extraction_summary() -> Any:
    """
    Filters returned dataframe from 'all_extraction_summary' by latest timestamp found in
    green-db table.

    Returns:
        Dataframe: with number of products by country and merchant for latest timestamps in green-db
        table.
    """
    return all_extraction_summary()[
        (all_extraction_summary()["timestamp"] >= green_db.get_latest_timestamp())
    ]


def products_by_category() -> tuple:
    """
    Gets 'get_category_summary' output, converts it in a dataframe and creates a bar chart for
    products per category.

    Returns:
        List: [plotly chart, pandas dataframe]
    """
    df = pd.DataFrame(green_db.get_category_summary(), columns=["category", "merchant", "products"])
    df_products_by_category = df.pivot_table(
        values="products", index=["category"], columns="merchant", fill_value=0
    )
    fig_products_by_category = px.bar(
        df, x="category", y="products", color="merchant", text="products"
    )
    return fig_products_by_category, df_products_by_category


def all_timestamps_merchant() -> tuple:
    """
    Concatenates 'all_extraction_summary' and 'all_scraping_summary' dataframes and creates a
    line chart for extracted and scraped products for all timestamps found by merchant and country.

    Returns:
        List: [plotly chart, pandas dataframe, pandas dataframe]
    """
    extraction = all_extraction_summary()
    extraction["type"] = "extraction"
    scraping = all_scraping_summary()
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
        .sort_values(by="date", ascending=False)
    )
    fig_timestamps_by_merchant = px.line(
        all_timestamps, x="date", y="products", color="merchant", symbol="type"
    )
    return fig_timestamps_by_merchant, df_timestamps_by_merchant, df_timestamps_by_merchant_country


def all_timestamps_agg() -> tuple:
    """
    Creates an aggregated view of 'all_timestamps_merchant'. Resulting objects show total
    number of extracted and scraped products for all timestamps found.

    Returns:
        List: [plotly chart, pandas dataframe]
    """
    df_timestamps_agg = (
        all_timestamps_merchant()[2]
        .pivot_table(
            values="products", index=["date"], columns="type", aggfunc=np.sum, fill_value=0
        )
        .sort_values(by="date", ascending=False)
    )
    timestamps = df_timestamps_agg.index
    fig_timestamps_agg = go.Figure()
    fig_timestamps_agg.add_trace(
        go.Bar(
            x=timestamps, y=df_timestamps_agg["extraction"], name="Extraction", marker_color="green"
        )
    )
    fig_timestamps_agg.add_trace(
        go.Bar(
            x=timestamps, y=df_timestamps_agg["scraping"], name="Scraping", marker_color="goldenrod"
        )
    )
    return fig_timestamps_agg, df_timestamps_agg


def products_by_label() -> tuple:
    """
    Gets 'products_by_sustainability_label' from green-db table, counts products with
    "certificate:UNKNOWN" and products with any other label and creates a dataframe and a line
    chart from it. It also filters given query to present products by sustainability label(s)
    from last product extraction in a dataframe.

    Returns:
        List: [plotly chart, pandas dataframe, pandas dataframe]
    """
    query = green_db.products_by_sustainability_label()
    unknown = []
    known = []
    for row in query:
        for item in row:
            if type(item) is list:
                for label in item:
                    if label == "certificate:UNKNOWN": unknown.append(row)
                    else: known.append(row)
    unknown_df = pd.DataFrame(unknown, columns=["timestamp", "labels", "count"])
    unknown_df["date"] = pd.to_datetime(unknown_df["timestamp"]).dt.date
    unknown_cumm = unknown_df.groupby("date").sum()
    unknown_cumm["label"] = "certificate:UNKNOWN"
    known_df = pd.DataFrame(known, columns=["timestamp", "labels", "count"])
    known_df["date"] = pd.to_datetime(known_df["timestamp"]).dt.date
    known_cumm = known_df.groupby("date").sum()
    known_cumm["label"] = "Known certificates"
    join_df = pd.concat([unknown_cumm, known_cumm]).reset_index()
    fig_label_unknown = px.line(join_df, x="date", y="count", color="label", text="count")
    df_label_unknown = join_df.pivot_table(
        values="count", index=["date"], columns="label", aggfunc=np.sum, fill_value=0
    ).sort_values(by="date", ascending=False)
    all = pd.DataFrame(query, columns=["timestamp", "labels", "count"])
    last_extraction = all[(all["timestamp"] >= green_db.get_latest_timestamp())].sort_values(
        "count", ascending=False
    )
    return fig_label_unknown, df_label_unknown, last_extraction[["labels", "count"]]


def products_unknown_label() -> Any:
    """
    Gets 'products_by_sustainability_label_timestamp' for last timestamp found in green-db table
    and filter products with "certificate:UNKNOWN".

    Returns:
        Dataframe: listing product id, name, merchant, url and sustainability label(s)
    """
    query = green_db.products_by_sustainability_label_timestamp(green_db.get_latest_timestamp())
    unknown = []
    for row in query:
        for item in row:
            if type(item) is list:
                for label in item:
                    if label == "certificate:UNKNOWN": unknown.append(row)
    return pd.DataFrame(unknown, columns=["id", "timestamp", "merchant", "name", "url", "labels"])
