import numpy as np
import pandas as pd
import plotly.express as px
from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import Scraping
from plotly.graph_objs import Figure


def get_latest_extraction_objects(df: pd.DataFrame) -> dict:
    """
    Fetch number of extracted products for latest available timestamp by merchant. Counts number
    of merchants.

    Returns:
        Dict: with objects to display in the monitoring app.
    """
    return {
        "df": df,
        "total_extracted": df["product_count"].sum(),
        "number_merchants": len(df.groupby("merchant")),
    }


def get_latest_scraping_objects() -> dict:
    """
    TODO
    Uses 'get_latest_scraping_summary' to fetch number of scraped products for latest
    available timestamp by merchant, query all tables in ScrapingDB and concatenates the result in a
    single dataframe.

    Args:
        connection_for_table (dict): Contains connection for ScrapingDB tables.

    Returns:
        Dict: with objects to display in the monitoring app.
    """

    all_scraping = [
        Scraping(table_name).get_latest_scraped_page_count_per_merchant_and_country()
        for table_name in ALL_SCRAPING_TABLE_NAMES
    ]
    df = pd.concat(all_scraping)
    return {"df": df, "total_scraped": df["scraped_page_count"].sum()}


def get_products_by_category_objects(query: pd.DataFrame) -> dict:
    """
    Uses 'get_latest_category_summary' output to create a bar chart for products per category
    and a pivot table. Counts number of categories.

    Args:
        query (pd.DataFrame): Data to plot.

    Returns:
        Dict: with objects to display in the monitoring app.
    """
    return {
        "chart": px.bar(
            query, x="category", y="product_count", color="merchant", text="product_count"
        ),
        "number_categories": len(query.groupby("category")),
    }


def get_all_timestamps_objects(extraction: pd.DataFrame) -> dict:
    """
    TODO
    Concatenates 'all_extraction_summary' and 'all_scraping_summary' dataframes to create:
    1) Line chart for extracted and scraped products for all timestamps found by
    merchant.
    2) Line chart for extracted and scraped products for all timestamps.
    3) Join DataFrame.

    Args:
        extraction (pd.DataFrame): Data to plot.
        connection_for_table (dict): Contains connection for ScrapingDB tables.

    Returns:
        Dict: with objects to display in the monitoring app.
    """
    extraction["type"] = "extraction"
    all_scraping = [
        Scraping(table_name).get_latest_scraped_page_count_per_merchant_and_country()
        for table_name in ALL_SCRAPING_TABLE_NAMES
    ]
    scraping = pd.concat(all_scraping)
    scraping["type"] = "scraping"
    all_timestamps_concat = pd.concat([extraction, scraping], ignore_index=True)
    all_timestamps_concat["date"] = pd.to_datetime(all_timestamps_concat["timestamp"]).dt.date
    df_agg_merchant = (
        all_timestamps_concat.groupby(by=["date", "merchant", "type"]).sum().reset_index()
    )
    df_agg_timestamp = all_timestamps_concat.groupby(by=["date", "type"]).sum().reset_index()
    pivot = (
        all_timestamps_concat.groupby(by=["date", "merchant", "country", "type"])
        .sum()
        .pivot_table(
            values="product_count",
            index=["date", "merchant", "country"],
            columns="type",
            aggfunc=np.sum,
            fill_value=0,
        )
        .sort_values(by="date", ascending=False)
    )
    return {
        "chart_by_merchant": px.line(
            df_agg_merchant, x="date", y="product_count", color="merchant", symbol="type"
        ),
        "chart_by_timestamp": px.line(df_agg_timestamp, x="date", y="product_count", color="type"),
        "pivot_timestamps_by_merchant_country": pivot,
    }


def create_plot_products_with_unknown_sustainability_label(
    query: pd.DataFrame,
) -> Figure:
    """
    TODO

    Args:
        query (pd.DataFrame): Data to plot.

    Returns:
        Figure: line chart to display in the monitoring app.
    """
    query["date"] = pd.to_datetime(query["timestamp"]).dt.date
    return px.line(query, x="date", y="product_count")
