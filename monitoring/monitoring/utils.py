import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from typing import Any
from database.connection import GreenDB
from monitoring import CONNECTION_FOR_TABLE

green_db = GreenDB()


def dates() -> Any:
    last_extraction = green_db.get_latest_timestamp().date()
    last_label_update = green_db.last_update_sustainability_labels().date()
    return last_extraction, last_label_update


# Scraping DB queries
def all_scraping_summary() -> Any:
    all_scraping = []
    [all_scraping.extend(value.get_scraping_summary()) for value in CONNECTION_FOR_TABLE.values()]
    return pd.DataFrame(
        all_scraping, columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")


def last_scraping_summary() -> Any:
    return all_scraping_summary()[
        (all_scraping_summary()["timestamp"] >= green_db.get_latest_timestamp())
    ]


# Extraction DB queries
def all_extraction_summary() -> Any:
    return pd.DataFrame(
        green_db.get_extraction_summary(), columns=["merchant", "timestamp", "products", "country"]
    ).sort_values(by="merchant")


def last_extraction_summary() -> Any:
    return all_extraction_summary()[
        (all_extraction_summary()["timestamp"] >= green_db.get_latest_timestamp())
    ]


def products_by_category() -> Any:
    df = pd.DataFrame(green_db.get_category_summary(), columns=["category", "merchant", "products"])
    df_products_by_category = df.pivot_table(
        values="products", index=["category"], columns="merchant", fill_value=0
    )
    fig_products_by_category = px.bar(
        df, x="category", y="products", color="merchant", text="products"
    )
    return fig_products_by_category, df_products_by_category


# Both scraping and extraction
def all_timestamps_merchant() -> Any:
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


def all_timestamps_agg() -> Any:
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


def products_by_label() -> Any:
    query = green_db.products_by_sustainability_label()
    all = pd.DataFrame(query, columns=["timestamp", "labels", "count"])
    last_extraction = all[(all["timestamp"] >= green_db.get_latest_timestamp())].sort_values(
        "count", ascending=False
    )
    unknown = []
    known = []
    for row in query:
        for item in row:
            if type(item) is list:
                [
                    unknown.append(row) if label == "certificate:UNKNOWN" else known.append(row)
                    for label in item
                ]

    unknown_df = pd.DataFrame(unknown, columns=["timestamp", "labels", "count"])
    unknown_df["date"] = pd.to_datetime(unknown_df["timestamp"]).dt.date
    unknown_cumm = unknown_df.groupby("date").sum()
    unknown_cumm["label"] = "certificate:UNKNOWN"
    known_df = pd.DataFrame(known, columns=["timestamp", "labels", "count"])
    known_df["date"] = pd.to_datetime(known_df["timestamp"]).dt.date
    known_cumm = known_df.groupby("date").sum()
    known_cumm["label"] = "Known certificates"
    join_df = pd.concat([unknown_cumm, known_cumm]).reset_index()
    fig = px.line(join_df, x="date", y="count", color="label", text="count")
    pivot = join_df.pivot_table(
        values="count", index=["date"], columns="label", aggfunc=np.sum, fill_value=0
    ).sort_values(by="date", ascending=False)
    return fig, pivot, last_extraction[["labels", "count"]]


def products_unknown_label() -> Any:
    query = green_db.products_by_sustainability_label_timestamp(green_db.get_latest_timestamp())
    unknown = []
    for row in query:
        for item in row:
            if type(item) is list:
                [unknown.append(row) for label in item if label == "certificate:UNKNOWN"]
    return pd.DataFrame(
        unknown, columns=["id", "timestamp", "merchant", "name", "url", "labels"]
    )
