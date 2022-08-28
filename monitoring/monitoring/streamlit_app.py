import streamlit as st

from monitoring.utils import (
    all_timestamps_agg,
    all_timestamps_merchant,
    dates,
    last_extraction_summary,
    last_scraping_summary,
    products_by_category,
    products_by_label,
    products_unknown_label,
)

st.set_page_config(page_icon="♻️", page_title="GreenDB")


def main():
    """
    This function renders streamlit application, uses dataframes and charts from 'utils'.
    """
    st.title("GreenDB")
    st.header("A Product-by-Product Sustainability Database")
    st.subheader("DB Summary")

    with st.sidebar:
        st.title("Overview")
        st.write("From last data extraction on:")
        st.write(dates()[0])
        st.metric(
            label="Number extracted products",
            value=last_extraction_summary()["products"].sum(),
        )
        st.metric(
            label="Number scraped products",
            value=last_scraping_summary()["products"].sum(),
        )
        st.metric(
            label="Number of categories", value=len(products_by_category()[1].groupby("category"))
        )
        st.metric(
            label="Number of merchants", value=len(last_extraction_summary().groupby("merchant"))
        )

    st.write("Latest data extraction overview by merchant:")
    ext_df, scr_df = st.tabs(["📀Extraction", " 🤖Scraping"])
    ext_df.dataframe(last_extraction_summary())
    scr_df.dataframe(last_scraping_summary())

    st.write("Categories by merchant")
    cat_chart, cat_df = st.tabs(["📊Chart", "📓Data"])
    cat_chart.plotly_chart(products_by_category()[0])
    cat_df.dataframe(products_by_category()[1])

    st.subheader("All timestamps Summary")
    st.write("Scraping and Extraction all timestamps")
    alltimes_chart, alltimes_df = st.tabs(["📊Chart", "📓Data"])
    alltimes_chart.plotly_chart(all_timestamps_agg()[0], use_container_width=True)
    alltimes_df.dataframe(all_timestamps_agg()[1])

    st.write("Scraping and Extraction all timestamps by merchant")
    chart, df_1, df_2 = st.tabs(["📊Chart", "📓Data by merchant", "📓Data by merchant and country"])
    chart.plotly_chart(all_timestamps_merchant()[0])
    df_1.dataframe(all_timestamps_merchant()[1])
    df_2.dataframe(all_timestamps_merchant()[2])

    st.subheader("Sustainability labels overview")
    sl1, sl2 = st.columns(2)
    sl1.write("Sustainability label's last update:")
    sl2.write(dates()[1])
    st.write("Products by sustainability label(s)")
    st.dataframe(products_by_label()[2])
    st.write("Unknown vs Known Sustainability labels for all timestamps")
    st.plotly_chart(products_by_label()[0], use_container_width=True)
    with st.expander("Display chart data"):
        st.table(products_by_label()[1])
    st.write("List of products with 'certificate:UNKNOWN'")
    st.dataframe(products_unknown_label())


main()
