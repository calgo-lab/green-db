import altair as alt
import streamlit as st

from monitoring.utils import (
    fetch_and_cache_latest_product_count_per_category_and_merchant,
    fetch_and_cache_latest_product_count_per_merchant_and_country,
    fetch_and_cache_latest_scraped_page_count_per_merchant_and_country,
    fetch_and_cache_product_count_by_sustainability_label_credibility_overtime,
    fetch_and_cache_product_count_with_unknown_sustainability_label,
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country,
    hash_greendb,
)


def render_sidebar() -> None:
    """
    Render streamlit sidebar from previously initialized cache. Sidebar provides a
        quick overview of the latest data extraction.
    """
    st.title("Overview")
    st.write("From last data extraction on:")
    st.write(
        fetch_and_cache_latest_product_count_per_merchant_and_country(hash_greendb())[
            "latest_extraction_timestamp"
        ]
    )

    st.metric(
        label="Number scraped pages",
        value=fetch_and_cache_latest_scraped_page_count_per_merchant_and_country()[
            "latest_scraping_number_of_scraped_pages"
        ],
    )

    st.metric(
        label="Number extracted products",
        value=fetch_and_cache_latest_product_count_per_merchant_and_country(hash_greendb())[
            "latest_extraction_number_of_products"
        ],
    )

    st.metric(
        label="Number of categories",
        value=fetch_and_cache_latest_product_count_per_category_and_merchant(hash_greendb())[
            "latest_extraction_number_of_categories"
        ],
    )

    st.metric(
        label="Number of merchants",
        value=fetch_and_cache_latest_product_count_per_merchant_and_country(hash_greendb())[
            "latest_extraction_number_of_merchants"
        ],
    )

    st.write("Sustainability label's last update:")
    st.write(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(hash_greendb())[
            "latest_sustainability_labels_timestamp"
        ]
    )


def render_basic_information() -> None:
    """
    Render 'basic information' from cache in streamlit. This is the main tab of the report,
        includes monitoring plots.
    """

    st.subheader("Scraped pages and extracted products")
    st.plotly_chart(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(hash_greendb())[
            "plot_scraped_vs_extracted_over_timestamp"
        ]
    )

    st.markdown("""---""")

    st.subheader("Scraped pages and extracted products by merchants")
    data_frame_scraped_page_and_product_count_per_merchant_and_country = (
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(hash_greendb())[
            "data_frame"
        ]
    )
    if "merchants_options" not in st.session_state:
        st.session_state["merchants_options"] = list(
            fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(hash_greendb())[
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
        fetch_and_cache_latest_product_count_per_category_and_merchant(hash_greendb())[
            "plot_latest_products_per_category_and_merchant"
        ]
    )

    st.markdown("""---""")

    fetch_and_cache_product_count_with_unknown_sustainability_label(hash_greendb())
    st.subheader("Products with UNKNOWN sustainability label")
    st.plotly_chart(
        fetch_and_cache_product_count_with_unknown_sustainability_label(hash_greendb())["plot"]
    )
    st.subheader("Credible vs 'certificate:OTHER' sustainability labels by merchant")
    st.caption(
        "Products with at least one label with credibility score >= 50 is considered "
        "credible. Products with certificate:OTHER are usually 3rd party labels not listed "
        "in our evaluation."
    )

    if "merchants_overtime_options" not in st.session_state:
        st.session_state["merchants_overtime_options"] = list(
            fetch_and_cache_product_count_by_sustainability_label_credibility_overtime(
                hash_greendb()
            )["merchant"].unique()
        )
    st.session_state["selected_merchants_overtime"] = st.multiselect(
        "Filter by merchant:",
        st.session_state["merchants_overtime_options"],
        st.session_state["merchants_overtime_options"][:],
    )

    st.session_state["plot_product_count_by_sustainability_label_credibility_all_timestamps"] = (
        alt.Chart(
            fetch_and_cache_product_count_by_sustainability_label_credibility_overtime(
                hash_greendb()
            )[
                fetch_and_cache_product_count_by_sustainability_label_credibility_overtime(
                    hash_greendb()
                ).isin(st.session_state["selected_merchants_overtime"])
            ]
        )
        .mark_line()
        .encode(
            x="timestamp", y=alt.Y("product_count", stack=None), color="merchant", strokeDash="type"
        )
    )
    st.altair_chart(
        st.session_state["plot_product_count_by_sustainability_label_credibility_all_timestamps"],
        use_container_width=True,
    )


def main() -> None:
    """
    This represents the basic structure of the Monitoring App page.
    """
    st.set_page_config(page_title="GreenDB", page_icon="♻️")
    st.title("GreenDB - A Product-by-Product Sustainability Database")
    with st.sidebar:
        render_sidebar()

    render_basic_information()


main()
