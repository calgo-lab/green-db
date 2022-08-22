import os
os.environ["POSTGRES_SCRAPING_USER"] = "scraping"
os.environ["POSTGRES_SCRAPING_PASSWORD"] = "scraping1992"
os.environ["POSTGRES_SCRAPING_HOST"] = "127.0.0.1"
os.environ["POSTGRES_SCRAPING_PORT"] = "5432"
os.environ["POSTGRES_GREEN_DB_USER"] = "green-db"
os.environ["POSTGRES_GREEN_DB_PASSWORD"] = "green1992"
os.environ["POSTGRES_GREEN_DB_HOST"] = "127.0.0.1"
os.environ["POSTGRES_GREEN_DB_PORT"] = "5432"

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.connection import GreenDB
from monitoring import CONNECTION_FOR_TABLE

green_db = GreenDB()

st.set_page_config(page_icon="♻️", page_title="GreenDB")


def extraction_summary_to_df(query):
    return pd.DataFrame(
        query, columns=["country", "merchant", "timestamp", "products"]
    ).sort_values(by="country")


def last_scraping_summary_to_df():
    return pd.DataFrame(
        [
            (CONNECTION_FOR_TABLE[table_name].get_last_job_summary()[0])
            for table_name in CONNECTION_FOR_TABLE
        ],
        columns=["country", "merchant", "timestamp", "products"],
    ).sort_values(by="country")


def all_scraping_summary_to_df():
    return pd.DataFrame(
        [
            (CONNECTION_FOR_TABLE[table_name].get_all_last_job()[0])
            for table_name in CONNECTION_FOR_TABLE
        ],
        columns=["country", "merchant", "timestamp", "products"],
    ).sort_values(by="country")


def category_stack_bars(df):
    fig = px.bar(df, x="category", y="products", color="merchant", text="products")
    return fig


def all_timestamps_merchant():
    """
    Gets all timestamps by merchant for green_bd and extraction databases.

    Args:
        timestamp (datetime): `timestamp` to check availability

    Returns:
        bool: Whether `timestamp` is available
    """
    extraction = extraction_summary_to_df(green_db.get_all_last_job())
    extraction["type"] = "extraction"
    scraping = all_scraping_summary_to_df()
    scraping["type"] = "scraping"
    all_timestamps = pd.concat([extraction, scraping], ignore_index=True)
    all_timestamps["date"] = pd.to_datetime(all_timestamps["timestamp"]).dt.date
    return all_timestamps


def all_timestamps_merchant_chart():
    df = all_timestamps_merchant()
    fig = px.line(df, x="date", y="products", color="merchant", symbol="type")
    return fig


def all_timestamps_df():
    all_timestamps_df = all_timestamps_merchant().pivot_table(
        values="products", index=["date"], columns="type", aggfunc=np.sum, fill_value=0
    )
    return all_timestamps_df


def all_timestamps_chart(df):
    timestamps = df.index
    all_timestamps_fig = go.Figure()
    all_timestamps_fig.add_trace(
        go.Bar(x=timestamps, y=df["extraction"], name="Extraction", marker_color="green")
    )
    all_timestamps_fig.add_trace(
        go.Bar(x=timestamps, y=df["scraping"], name="Scraping", marker_color="goldenrod")
    )
    return all_timestamps_fig


def labels_summary_chart():
    df = green_db.products_by_label()
    fig = px.line(df, x="date", y="count", color="label", text="count")
    return fig

def main():
    st.title("GreenDB")
    st.header("A Product-by-Product Sustainability Database")
    st.subheader("Green-DB Summary")
    h1, h2 = st.columns(2)
    h1.write("Latest timestamp of data extraction:")
    h2.write(green_db.get_latest_timestamp().date())

    m1, m2, m3 = st.columns(3)

    m1.metric(
        label="Number extracted of products",
        value=extraction_summary_to_df(green_db.get_last_job_summary())["products"].sum(),
    )
    m2.metric(
        label="Number of categories", value=len(green_db.get_category_summary().groupby("category"))
    )
    m3.metric(
        label="Number of merchants", value=len(green_db.get_category_summary().groupby("merchant"))
    )

    st.write("Latest job summary by merchant")
    summary_ext, summary_scr = st.tabs(["📀Extraction", " 🤖Scraping"])
    summary_ext.dataframe(extraction_summary_to_df(green_db.get_last_job_summary()))
    summary_scr.dataframe(last_scraping_summary_to_df())

    st.write("Categories by merchant")
    cat_chart, cat_df = st.tabs(["📊Chart", "📓Data"])
    cat_chart.plotly_chart(
        category_stack_bars(green_db.get_category_summary()), use_container_width=True
    )
    cat_df.dataframe(
        green_db.get_category_summary().pivot_table(
            values="products", index=["category"], columns="merchant", fill_value=0
        )
    )

    st.write("Scraping and Extraction all timestamps")
    alltimes_chart, alltimes_df = st.tabs(["📊Chart", "📓Data"])
    alltimes_chart.plotly_chart(all_timestamps_chart(all_timestamps_df()), use_container_width=True)
    alltimes_df.dataframe(all_timestamps_df())

    st.write("Scraping and Extraction all timestamps by merchant")
    alltimesmer_chart, alltimesmer_df = st.tabs(["📊Chart", "📓Data"])
    alltimesmer_chart.plotly_chart(all_timestamps_merchant_chart())
    alltimesmer_df.dataframe(all_timestamps_merchant())

    st.subheader("Sustainability labels overview")
    sus1, sus2, sus3 = st.columns(3)
    sus1.write("Sustainability label's last update:")
    sus2.write(green_db.last_update_sustainability_labels())
    st.write("Unknown vs Known Sustainability labels")
    st.plotly_chart(labels_summary_chart(), use_container_width=True)


main()
