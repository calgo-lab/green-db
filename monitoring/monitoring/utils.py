import pandas as pd
import plotly.express as px
import streamlit as st
from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import GreenDB, Scraping
from database.tables import SustainabilityLabelsTable

from monitoring.utils_old import get_all_timestamps_objects


def fetch_and_cache_latest_product_count_per_merchant_and_country(green_db: GreenDB) -> None:
    """
    TODO

    Args:
        green_db (GreenDB): _description_
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
    TODO
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
    TODO

    Args:
        green_db (GreenDB): _description_
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
    TODO

    Args:
        green_db (GreenDB): _description_
    """
    if "data_frame_product_count_with_unknown_sustainability_label" not in st.session_state:
        st.session_state[
            "data_frame_product_count_with_unknown_sustainability_label"
        ] = green_db.get_product_count_with_unknown_sustainability_label()
        st.session_state["data_frame_product_count_with_unknown_sustainability_label"][
            "date"
        ] = st.session_state["data_frame_product_count_with_unknown_sustainability_label"][
            "timestamp"
        ].dt.date

        st.session_state["plot_product_count_with_unknown_sustainability_label"] = px.line(
            st.session_state["data_frame_product_count_with_unknown_sustainability_label"],
            x="date",
            y="product_count",
        )


def render_sidebar(green_db: GreenDB) -> None:
    """
    TODO

    Args:
        green_db (GreenDB): _description_
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
    TODO

    Args:
        green_db (GreenDB): _description_
    """
    if "all_timestamps" not in st.session_state:
        st.session_state.all_timestamps = get_all_timestamps_objects(
            green_db.get_product_count_per_merchant_and_country()
        )

    st.subheader("Scraped pages and extracted products")
    st.plotly_chart(st.session_state.all_timestamps["chart_by_timestamp"], use_container_width=True)

    st.markdown("""---""")

    st.subheader("Scraped pages and extracted products by merchants")
    st.plotly_chart(st.session_state.all_timestamps["chart_by_merchant"], use_container_width=True)

    st.markdown("""---""")

    st.subheader("Latest products per category and merchant")
    st.plotly_chart(st.session_state["plot_latest_products_per_category_and_merchant"])

    st.markdown("""---""")

    fetch_and_cache_product_count_with_unknown_sustainability_label(green_db)
    st.subheader("Products with UNKNOWN sustainability label")
    st.plotly_chart(
        st.session_state["plot_product_count_with_unknown_sustainability_label"],
        use_container_width=True,
    )


def render_extended_information(green_db: GreenDB) -> None:
    """
    TODO

    Args:
        green_db (GreenDB): _description_
    """
    if st.button("Do you want to fetch this data? - Could take a while."):

        st.subheader("Scraped pages vs. extracted products count as table")
        st.dataframe(st.session_state.all_timestamps["pivot_timestamps_by_merchant_country"])

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
