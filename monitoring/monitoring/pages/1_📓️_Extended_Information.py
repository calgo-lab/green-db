import streamlit as st

from monitoring.utils import (
    fetch_and_cache_extended_information,
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country,
    hash_greendb,
)


def render_extended_information() -> None:
    """
    Render dataframes from cache in streamlit. This is the secondary page of the monitoring report.
    """
    st.subheader("Scraped pages vs. extracted products count as table")
    st.dataframe(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(hash_greendb())[
            "pivot_scraped_vs_extracted"
        ].sort_values(by="timestamp", ascending=False)
    )

    st.markdown("""---""")

    st.subheader("Latest product count by sustainability label as table")
    st.write(
        "Number of sustainability labels in use:",
        len(
            fetch_and_cache_extended_information(hash_greendb())[
                "latest_product_count_per_sustainability_label"
            ]
        ),
    )
    st.dataframe(
        fetch_and_cache_extended_information(hash_greendb())[
            "latest_product_count_per_sustainability_label"
        ]
    )

    st.markdown("""---""")

    st.subheader("Latest products with UNKNOWN label as table")

    st.dataframe(
        fetch_and_cache_extended_information(hash_greendb())[
            "latest_products_with_unknown_sustainability_label"
        ]
    )


def main() -> None:
    """
    This represents the basic structure of the Extended Information page.
    """
    st.set_page_config(page_title="Extended Information", page_icon="♻️")
    render_extended_information()


main()
