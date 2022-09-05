import numpy as np
import pandas as pd
import plotly.express as px
from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import Scraping


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
    all_timestamps_concat["date"] = all_timestamps_concat["timestamp"].dt.date
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
