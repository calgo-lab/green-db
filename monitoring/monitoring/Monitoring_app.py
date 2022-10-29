import altair as alt
import streamlit as st

from database.connection import GreenDB
from database.tables import SustainabilityLabelsTable
from monitoring.utils import (
    fetch_and_cache_latest_product_count_per_category_and_merchant,
    fetch_and_cache_latest_product_count_per_merchant_and_country,
    fetch_and_cache_latest_scraped_page_count_per_merchant_and_country,
    fetch_and_cache_product_count_with_unknown_sustainability_label,
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country,
)

green_db = GreenDB()


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

    st.metric(
        label="Number scraped pages",
        value=fetch_and_cache_latest_scraped_page_count_per_merchant_and_country()[
            "latest_scraping_number_of_scraped_pages"
        ],
    )

    st.metric(
        label="Number extracted products",
        value=fetch_and_cache_latest_product_count_per_merchant_and_country(green_db)[
            "latest_extraction_number_of_products"
        ],
    )

    st.metric(
        label="Number of categories",
        value=fetch_and_cache_latest_product_count_per_category_and_merchant(green_db)[
            "latest_extraction_number_of_categories"
        ],
    )

    st.metric(
        label="Number of merchants",
        value=fetch_and_cache_latest_product_count_per_merchant_and_country(green_db)[
            "latest_extraction_number_of_merchants"
        ],
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

    st.subheader("Scraped pages and extracted products")
    st.plotly_chart(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)[
            "plot_scraped_vs_extracted_over_timestamp"
        ]
    )

    st.markdown("""---""")

    st.subheader("Scraped pages and extracted products by merchants")
    data_frame_scraped_page_and_product_count_per_merchant_and_country = (
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)[
            "data_frame"
        ]
    )
    st.session_state["merchants_options"] = list(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)[
            "data_frame"
        ]["merchant"].unique()
    )
    st.session_state["selected_merchants"] = st.multiselect(
        "Filter by merchant:",
        st.session_state["merchants_options"],
        st.session_state["merchants_options"][:],
    )
    st.altair_chart(
        alt.Chart(
            data_frame_scraped_page_and_product_count_per_merchant_and_country[
                data_frame_scraped_page_and_product_count_per_merchant_and_country.merchant.isin(
                    st.session_state["selected_merchants"]
                )
            ]
            .groupby(by=["timestamp", "merchant", "type"])
            .sum()
            .reset_index(),
        )
        .mark_line()
        .encode(
            x="timestamp",
            y="product_count",
            color="merchant",
            strokeDash="type",
        ),
        use_container_width=True,
    )

    st.markdown("""---""")

    st.subheader("Latest products per category and merchant")
    st.plotly_chart(
        fetch_and_cache_latest_product_count_per_category_and_merchant(green_db)[
            "plot_latest_products_per_category_and_merchant"
        ]
    )

    st.markdown("""---""")

    fetch_and_cache_product_count_with_unknown_sustainability_label(green_db)
    st.subheader("Products with UNKNOWN sustainability label")
    st.plotly_chart(
        fetch_and_cache_product_count_with_unknown_sustainability_label(green_db)["plot"]
    )


st.set_page_config(page_title="GreenDB", page_icon="♻️")
st.title("GreenDB - A Product-by-Product Sustainability Database")
# Sidebar with general overview of the project
with st.sidebar:
    render_sidebar(green_db)

render_basic_information(green_db)
