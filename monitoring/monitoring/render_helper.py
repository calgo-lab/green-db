import streamlit as st
from database.connection import GreenDB
from database.tables import SustainabilityLabelsTable

from monitoring.utils import (
    create_plot_products_with_unknown_sustainability_label,
    get_all_timestamps_objects,
    get_latest_extraction_objects,
    get_latest_scraping_objects,
    get_products_by_category_objects,
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

    if "latest_extraction" not in st.session_state:
        st.session_state.latest_extraction = get_latest_extraction_objects(
            green_db.get_latest_product_count_per_merchant_and_country()
        )

    st.metric(
        label="Number extracted products",
        value=st.session_state.latest_extraction["total_extracted"],
    )

    if "latest_scraping" not in st.session_state:
        st.session_state.latest_scraping = get_latest_scraping_objects()

    st.metric(
        label="Number scraped pages",
        value=st.session_state.latest_scraping["total_scraped"],
    )

    if "extraction_by_category" not in st.session_state:
        st.session_state.extraction_by_category = get_products_by_category_objects(
            green_db.get_latest_product_count_per_category_and_merchant()
        )

    st.metric(
        label="Number of categories",
        value=st.session_state.extraction_by_category["number_categories"],
    )

    st.metric(
        label="Number of merchants",
        value=st.session_state.latest_extraction["number_merchants"],
    )

    st.metric(
        label="Number scraped pages",
        value=st.session_state.latest_scraping["total_scraped"],
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
    st.plotly_chart(st.session_state.extraction_by_category["chart"])

    st.markdown("""---""")

    st.subheader("Products with UNKNOWN sustainability label")
    if "plot_products_with_unknown_sustainability_label" not in st.session_state:
        st.session_state.plot_products_with_unknown_sustainability_label = (
            create_plot_products_with_unknown_sustainability_label(
                green_db.get_product_count_with_unknown_sustainability_label()
            )
        )
    st.plotly_chart(
        st.session_state.plot_products_with_unknown_sustainability_label,
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
