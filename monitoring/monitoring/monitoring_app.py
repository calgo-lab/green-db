import streamlit as st

from database.connection import GreenDB
from database.tables import SustainabilityLabelsTable
from monitoring.utils import (
    get_all_timestamps_objects,
    get_known_vs_unknown_certificates_chart,
    get_latest_extraction_objects,
    get_latest_scraping_objects,
    get_products_by_category_objects,
)

green_db = GreenDB()


def main() -> None:
    """
    This function renders streamlit application, uses methods from 'utils' to create a project
    report. Holds connection to the database.
    """
    # Header section with titles
    st.set_page_config(page_icon="♻️", page_title="GreenDB")
    st.title("GreenDB")
    st.header("A Product-by-Product Sustainability Database")
    st.subheader("DB Summary")

    # Adds first session states
    if "latest_extraction" not in st.session_state:
        st.session_state.latest_extraction = get_latest_extraction_objects(
            green_db.get_latest_extraction_summary()
        )
    if "latest_scraping" not in st.session_state:
        st.session_state.latest_scraping = get_latest_scraping_objects()
    if "extraction_by_category" not in st.session_state:
        st.session_state.extraction_by_category = get_products_by_category_objects(
            green_db.get_latest_category_summary()
        )

    # Sidebar with general overview of the project
    with st.sidebar:
        st.title("Overview")
        st.write("From last data extraction on:")
        st.write(green_db.get_latest_timestamp().date())
        st.metric(
            label="Number extracted products",
            value=st.session_state.latest_extraction["total_extracted"],
        )
        st.metric(
            label="Number scraped products",
            value=st.session_state.latest_scraping["total_scraped"],
        )
        st.metric(
            label="Number of categories",
            value=st.session_state.extraction_by_category["number_categories"],
        )
        st.metric(
            label="Number of merchants",
            value=st.session_state.latest_extraction["number_merchants"],
        )
        st.write("Sustainability label's last update:")
        st.write(green_db.get_latest_timestamp(SustainabilityLabelsTable).date())

    # Tabs with latest summary of extracted and scraped products.
    st.write("Latest data extraction overview by merchant:")
    tab1, tab2 = st.tabs(["📀Extraction", " 🤖Scraping"])
    with tab1:
        st.dataframe(st.session_state.latest_extraction["df"])
    with tab2:
        st.dataframe(st.session_state.latest_scraping["df"])

    # Main container, contains all the plots
    with st.container():
        if "all_timestamps" not in st.session_state:
            st.session_state.all_timestamps = get_all_timestamps_objects(
                green_db.get_extraction_summary()
            )
        st.subheader("All timestamps Summary")
        st.write("Scraping and Extraction all timestamps")
        st.plotly_chart(
            st.session_state.all_timestamps["chart_by_timestamp"], use_container_width=True
        )
        st.write("Scraping and Extraction all timestamps by merchant")
        st.plotly_chart(
            st.session_state.all_timestamps["chart_by_merchant"], use_container_width=True
        )
        if st.button("Show detailed dataframe by merchant and country for all timestamps."):
            st.dataframe(st.session_state.all_timestamps["pivot_timestamps_by_merchant_country"])
        st.write("Products by category and merchant")
        st.plotly_chart(st.session_state.extraction_by_category["chart"])
        st.write("Unknown vs Known certificates for all timestamps")
        st.plotly_chart(
            get_known_vs_unknown_certificates_chart(green_db.get_known_vs_unknown_certificates()),
            use_container_width=True,
        )
        st.write("List of products with 'certificate:UNKNOWN'")
        st.caption("From latest available timestamp")
        if st.button("Show list of products"):
            st.dataframe(green_db.get_latest_products_certificate_unknown())

    # Last container to show dataframe of products by label
    with st.container():
        st.write("Products by sustainability label(s)")
        if st.button("Show list of labels"):
            st.dataframe(green_db.get_latest_products_by_label())


main()
