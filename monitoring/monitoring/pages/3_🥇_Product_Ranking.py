import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    fetch_and_cache_latest_product_count_per_category_and_merchant,
    fetch_and_cache_leaderboards,
    fetch_and_cache_product_families,
)

green_db = GreenDB()


def update_categories():
    if st.session_state.radio == "all":
        st.session_state["categories_options"] = fetch_and_cache_product_families(green_db)[
            "all_categories"
        ]
    elif st.session_state.radio == "electronics":
        st.session_state["categories_options"] = fetch_and_cache_product_families(green_db)[
            "electronics"
        ]
    elif st.session_state.radio == "fashion":
        st.session_state["categories_options"] = fetch_and_cache_product_families(green_db)[
            "fashion"
        ]


def render_product_ranking_filters_as_sidebar() -> None:
    if "categories_options" not in st.session_state:
        st.session_state["categories_options"] = list(
            fetch_and_cache_latest_product_count_per_category_and_merchant(green_db)["df"][
                "category"
            ].unique()
        )

    st.radio(
        label="Select product family:",
        options=["all", "electronics", "fashion"],
        key="radio",
        on_change=update_categories,
    )

    number_of_products_to_fetch = st.number_input(
        "Choose number of products to fetch (max 10k)", min_value=30, max_value=10000, step=10
    )
    st.session_state["number_of_products_to_fetch"] = number_of_products_to_fetch

    if "merchants_options" not in st.session_state:
        st.session_state["merchants_options"] = list(
            fetch_and_cache_leaderboards(green_db)["rank_by_merchant"]["merchant"].unique()
        )
    st.session_state["merchant_filter"] = st.multiselect(
        label="Filter by merchant",
        options=st.session_state["merchants_options"],
        default=st.session_state["merchants_options"][:],
    )


def render_product_ranking() -> None:
    st.subheader("Top sustainable products in GreenDB")
    st.caption("From all unique products in the database with credible sustainability labels.")
    st.session_state["category_filter"] = st.multiselect(
        label="Filter by category",
        options=st.session_state["categories_options"],
        default=st.session_state["categories_options"][:],
    )

    credibility_button, credibility_text = st.columns(2)
    credibility_text.caption("Products ranked by their mean credibility score.")
    if credibility_button.button("Fetch top products based on credibility"):
        st.session_state["rank_by"] = "credibility"

    sustainability_score_button, sustainability_score_text = st.columns(2)
    sustainability_score_text.caption(
        "Products ranked by their sustainability score, calculated as the mean of "
        "means of ecological and social values."
    )
    if sustainability_score_button.button("Fetch top products by sustainability score"):
        st.session_state["rank_by"] = "sustainability_score"

    if "rank_by" in st.session_state:
        data_frame_top_products = green_db.get_top_products_by_credibility_or_sustainability_score(
            st.session_state["merchant_filter"],
            st.session_state["category_filter"],
            st.session_state["number_of_products_to_fetch"],
            st.session_state["rank_by"],
        )
        st.dataframe(data_frame_top_products)
        st.session_state["categories_options"] = data_frame_top_products["category"].unique()

        st.download_button(
            label="Download product sample CSV",
            data=data_frame_top_products.to_csv().encode("utf-8"),
            file_name="green_db_sample.csv",
            mime="text/csv",
        )


def main() -> None:
    st.set_page_config(page_title="Product Ranking", page_icon="♻️")
    with st.sidebar:
        render_product_ranking_filters_as_sidebar()
    render_product_ranking()


main()
