import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    fetch_and_cache_extended_information,
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country,
)

green_db = GreenDB()


def render_extended_information(green_db: GreenDB) -> None:
    """
    Render dataframes from session states in streamlit just when user clicks to fetch the data.
        This is the secondary tab of the report.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    st.subheader("Scraped pages vs. extracted products count as table")
    st.dataframe(
        fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)[
            "pivot_scraped_vs_extracted"
        ].sort_values(by="timestamp", ascending=False)
    )

    st.markdown("""---""")

    st.subheader("Latest product count by sustainability label as table")
    st.write(
        "Number of sustainability labels in use:",
        len(
            fetch_and_cache_extended_information(green_db)[
                "latest_product_count_per_sustainability_label"
            ]
        ),
    )
    st.dataframe(
        fetch_and_cache_extended_information(green_db)[
            "latest_product_count_per_sustainability_label"
        ]
    )

    st.markdown("""---""")

    st.subheader("Latest products with UNKNOWN label as table")

    st.dataframe(
        fetch_and_cache_extended_information(green_db)[
            "latest_products_with_unknown_sustainability_label"
        ]
    )
    st.dataframe(green_db.get_product_count_by_sustainability_label_credibility_alltimestamps())


st.set_page_config(page_title="Extended Information", page_icon="♻️")
render_extended_information(green_db)
