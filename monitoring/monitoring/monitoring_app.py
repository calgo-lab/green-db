import streamlit as st

from monitoring.utils import (
    all_timestamps,
    dates,
    labels_known_vs_unknown,
    latest_extraction_summary,
    latest_scraping_summary,
    products_by_category,
    products_by_label,
)


def main() -> None:
    """
    This function renders streamlit application, uses dataframes and charts from 'utils'.
    """
    st.set_page_config(page_icon="♻️", page_title="GreenDB")
    st.title("GreenDB")
    st.header("A Product-by-Product Sustainability Database")
    st.subheader("DB Summary")

    last_timestamps = dates()
    latest_extraction_obj = latest_extraction_summary()
    latest_scraping_obj = latest_scraping_summary()
    cat_obj = products_by_category()

    with st.sidebar:
        st.title("Overview")
        st.write("From last data extraction on:")
        st.write(last_timestamps[0])
        st.metric(
            label="Number extracted products",
            value=latest_extraction_obj[1],
        )
        st.metric(
            label="Number scraped products",
            value=latest_scraping_obj[1],
        )
        st.metric(label="Number of categories", value=cat_obj[2])
        st.metric(label="Number of merchants", value=latest_extraction_obj[2])

    st.write("Latest data extraction overview by merchant:")
    ext_df, scr_df = st.tabs(["📀Extraction", " 🤖Scraping"])
    ext_df.dataframe(latest_extraction_obj[0])
    scr_df.dataframe(latest_scraping_obj[0])

    st.write("Categories by merchant")
    cat_chart, cat_df = st.tabs(["📊Chart", "📓Data"])
    cat_chart.plotly_chart(cat_obj[0])
    cat_df.dataframe(cat_obj[1])

    st.subheader("All timestamps Summary")
    all_timestamps_obj = all_timestamps()
    st.write("Scraping and Extraction all timestamps")
    alltimes_chart, alltimes_df = st.tabs(["📊Chart", "📓Data"])
    alltimes_chart.plotly_chart(all_timestamps_obj[3], use_container_width=True)
    alltimes_df.dataframe(all_timestamps_obj[4])

    st.write("Scraping and Extraction all timestamps by merchant")
    chart, df_1, df_2 = st.tabs(["📊Chart", "📓Data by merchant", "📓Data by merchant and country"])
    chart.plotly_chart(all_timestamps_obj[0])
    df_1.dataframe(all_timestamps_obj[1])
    df_2.dataframe(all_timestamps_obj[2])

    st.subheader("Sustainability labels overview")
    sl1, sl2 = st.columns(2)
    sl1.write("Sustainability label's last update:")
    sl2.write(last_timestamps[1])
    st.write("Products by sustainability label(s)")
    label_df = products_by_label()
    st.dataframe(label_df)
    st.write("Unknown vs Known Sustainability labels for all timestamps")
    unknown_certificates_obj = labels_known_vs_unknown()
    st.plotly_chart(unknown_certificates_obj[0], use_container_width=True)
    with st.expander("Display chart data"):
        st.table(unknown_certificates_obj[1])
    st.write("List of products with 'certificate:UNKNOWN'")
    st.dataframe(unknown_certificates_obj[2])


main()
