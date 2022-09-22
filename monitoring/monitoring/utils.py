import pandas as pd
import plotly.express as px
import streamlit as st

from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import GreenDB, Scraping
from database.tables import SustainabilityLabelsTable


def fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(
    green_db: GreenDB,
) -> None:
    """
    Fetch product count and scraped pages per merchant and country for all timestamps. Save
        objects in streamlit cache: pd.DataFrame with queried data and linear plotly
        charts for scraped pages vs extracted product over timestamp and over timestamp per
        merchant.


    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_scraped_page_and_product_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_product_count_per_merchant_and_country"
        ] = green_db.get_product_count_per_merchant_and_country()
        st.session_state["data_frame_product_count_per_merchant_and_country"]["type"] = "extract"

        st.session_state["data_frame_scraped_page_count_per_merchant_and_country"] = pd.concat(
            [
                Scraping(table_name).get_scraped_page_count_per_merchant_and_country()
                for table_name in ALL_SCRAPING_TABLE_NAMES
            ]
        ).rename(columns={"scraped_page_count": "product_count"})
        st.session_state["data_frame_scraped_page_count_per_merchant_and_country"][
            "type"
        ] = "scraping"

        st.session_state[
            "data_frame_scraped_page_and_product_count_per_merchant_and_country"
        ] = pd.concat(
            [
                st.session_state["data_frame_scraped_page_count_per_merchant_and_country"],
                st.session_state["data_frame_product_count_per_merchant_and_country"],
            ],
            ignore_index=True,
        )

        # Plot and restructure the dataframe
        st.session_state["plot_scraped_vs_extracted_over_timestamp_per_merchant"] = px.line(
            st.session_state["data_frame_scraped_page_and_product_count_per_merchant_and_country"]
            .groupby(by=["timestamp", "merchant", "type"])
            .sum()
            .reset_index(),
            x="timestamp",
            y="product_count",
            color="merchant",
            symbol="type",
        )
        st.session_state["plot_scraped_vs_extracted_over_timestamp"] = px.line(
            st.session_state["data_frame_scraped_page_and_product_count_per_merchant_and_country"]
            .groupby(by=["timestamp", "type"])
            .sum()
            .reset_index(),
            x="timestamp",
            y="product_count",
            color="type",
        )
        st.session_state["pivot_scraped_vs_extracted"] = st.session_state[
            "data_frame_scraped_page_and_product_count_per_merchant_and_country"
        ].pivot_table(
            values="product_count",
            index=["timestamp", "merchant", "country"],
            columns="type",
            aggfunc=sum,
            fill_value=0,
        )


def fetch_and_cache_latest_product_count_per_merchant_and_country(green_db: GreenDB) -> None:
    """
    Fetch product count per merchant and country for latest timestamp available. Saves a
        pd.DataFrame with queried data, total number of extracted products and total number of
        unique merchants in streamlit cache.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_latest_product_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_latest_product_count_per_merchant_and_country"
        ] = green_db.get_latest_product_count_per_merchant_and_country()

        # and calculate some values for convenience
        st.session_state["latest_extraction_number_of_products"] = st.session_state[
            "data_frame_latest_product_count_per_merchant_and_country"
        ]["product_count"].sum()
        st.session_state["latest_extraction_number_of_merchants"] = len(
            st.session_state["data_frame_latest_product_count_per_merchant_and_country"].groupby(
                "merchant"
            )
        )


def fetch_and_cache_latest_scraped_page_count_per_merchant_and_country() -> None:
    """
    Fetch scraped pages per merchant and country for latest timestamp available. Saves in
        streamlit cache a pd.DataFrame with queried data for all tables in ScrapingDB and total
        number of scraped pages.
    """
    if "data_frame_latest_scraped_page_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_latest_scraped_page_count_per_merchant_and_country"
        ] = pd.concat(
            [
                Scraping(table_name).get_latest_scraped_page_count_per_merchant_and_country()
                for table_name in ALL_SCRAPING_TABLE_NAMES
            ]
        )

        # and calculate some values for convenience
        st.session_state["latest_scraping_number_of_scraped_pages"] = st.session_state[
            "data_frame_latest_scraped_page_count_per_merchant_and_country"
        ]["scraped_page_count"].sum()


def fetch_and_cache_latest_product_count_per_category_and_merchant(green_db: GreenDB) -> None:
    """
    Fetch product count per category per merchant for latest timestamp available. Save objects
        in streamlit cache: pd.DataFrame with queried data, total number of categories and bar
        chart for fetched data.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_latest_product_count_per_category_and_merchant" not in st.session_state:
        st.session_state[
            "data_frame_latest_product_count_per_category_and_merchant"
        ] = green_db.get_latest_product_count_per_category_and_merchant()

        st.session_state["latest_extraction_number_of_categories"] = len(
            st.session_state["data_frame_latest_product_count_per_category_and_merchant"].groupby(
                "category"
            )
        )

        st.session_state["plot_latest_products_per_category_and_merchant"] = px.bar(
            st.session_state["data_frame_latest_product_count_per_category_and_merchant"],
            x="category",
            y="product_count",
            color="merchant",
            text="product_count",
        )


def fetch_and_cache_product_count_with_unknown_sustainability_label(green_db: GreenDB) -> None:
    """
    Fetch product count for products by unknown and unknown sustainability label(s). Saves a
        pd.DataFrame and a line plot from queried data in streamlit cache.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_product_count_with_unknown_sustainability_label" not in st.session_state:
        st.session_state[
            "data_frame_product_count_with_unknown_sustainability_label"
        ] = green_db.get_product_count_with_unknown_sustainability_label()

        st.session_state["plot_product_count_with_unknown_sustainability_label"] = px.line(
            st.session_state["data_frame_product_count_with_unknown_sustainability_label"],
            x="timestamp",
            y="product_count",
        )


def render_sidebar(green_db: GreenDB) -> None:
    """
    Render streamlit sidebar from previously initialized session states. Sidebar provides a
        quick overview of the latest data extraction.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    st.title("Overview")
    st.write("From last data extraction on:")
    st.write(green_db.get_latest_timestamp().date())

    fetch_and_cache_latest_scraped_page_count_per_merchant_and_country()
    st.metric(
        label="Number scraped pages",
        value=st.session_state["latest_scraping_number_of_scraped_pages"],
    )

    fetch_and_cache_latest_product_count_per_merchant_and_country(green_db)
    st.metric(
        label="Number extracted products",
        value=st.session_state["latest_extraction_number_of_products"],
    )

    fetch_and_cache_latest_product_count_per_category_and_merchant(green_db)
    st.metric(
        label="Number of categories",
        value=st.session_state["latest_extraction_number_of_categories"],
    )

    st.metric(
        label="Number of merchants",
        value=st.session_state["latest_extraction_number_of_merchants"],
    )

    st.write("Sustainability label's last update:")
    st.write(green_db.get_latest_timestamp(SustainabilityLabelsTable).date())


def render_basic_information(green_db: GreenDB) -> None:
    """
    Render 'basic information' from previously initialized session states in streamlit. This is
        the main tab of the report, includes all plots.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)
    st.subheader("Scraped pages and extracted products")
    st.plotly_chart(st.session_state["plot_scraped_vs_extracted_over_timestamp"])

    st.markdown("""---""")

    st.subheader("Scraped pages and extracted products by merchants")
    st.plotly_chart(st.session_state["plot_scraped_vs_extracted_over_timestamp_per_merchant"])

    st.markdown("""---""")

    st.subheader("Latest products per category and merchant")
    st.plotly_chart(st.session_state["plot_latest_products_per_category_and_merchant"])

    st.markdown("""---""")

    fetch_and_cache_product_count_with_unknown_sustainability_label(green_db)
    st.subheader("Products with UNKNOWN sustainability label")
    st.plotly_chart(st.session_state["plot_product_count_with_unknown_sustainability_label"])


def render_extended_information(green_db: GreenDB) -> None:
    """
    Render dataframes from session states in streamlit just when user clicks to fetch the data.
        Secondary tab of the report.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if st.button("Do you want to fetch this data? - Could take a while."):

        st.subheader("Scraped pages vs. extracted products count as table")
        st.dataframe(st.session_state["pivot_scraped_vs_extracted"])

        st.markdown("""---""")

        st.subheader("Latest product count by sustainability label as table")
        if "latest_product_count_per_sustainability_label" not in st.session_state:
            st.session_state.latest_product_count_per_sustainability_label = (
                green_db.get_latest_product_count_per_sustainability_label()
            )
        st.dataframe(st.session_state.latest_product_count_per_sustainability_label)

        st.markdown("""---""")

        st.subheader("Latest products with UNKNOWN label as table")
        if "latest_products_with_unknown_sustainability_label" not in st.session_state:
            st.session_state.latest_products_with_unknown_sustainability_label = (
                green_db.get_latest_products_with_unknown_sustainability_label()
            )
        st.dataframe(st.session_state.latest_products_with_unknown_sustainability_label)
