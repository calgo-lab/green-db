import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    fetch_and_cache_category_ecological_vs_social_score,
    fetch_and_cache_leaderboards,
    fetch_and_cache_product_count_by_sustainability_label_credibility,
    fetch_and_cache_product_count_credible_sustainability_labels_by_category,
)

green_db = GreenDB()


def render_sidebar_leaderboards(green_db: GreenDB) -> None:
    data_frame_product_count_by_sustainability_label_credibility = (
        green_db.get_product_count_by_sustainability_label_credibility()
    )
    st.write(
        "All unique products",
        data_frame_product_count_by_sustainability_label_credibility["product_count"].sum(),
    )
    st.write(
        "Unique products with credibility",
        data_frame_product_count_by_sustainability_label_credibility[
            data_frame_product_count_by_sustainability_label_credibility.type == "credible"
        ]["product_count"].sum(),
    )
    st.write("All unique products by merchant")
    st.dataframe(
        data_frame_product_count_by_sustainability_label_credibility.groupby(["merchant"])
        .sum()
        .sort_values(by="product_count", ascending=False)
    )


def render_plots_product_count_by_credibility(green_db: GreenDB) -> None:
    st.header("GreenDB Leaderboards")
    st.subheader("Product credibility by merchant")
    st.caption(
        "Calculated from all unique products in the database. Where "
        "sustainability label credibility score >= 50 is credible and < 50 is not credible."
    )
    st.altair_chart(
        fetch_and_cache_product_count_by_sustainability_label_credibility(green_db)[
            "plot_normalized_product_count_w_vs_wo_credibility"
        ],
        use_container_width=True,
    )

    st.subheader("Product with credible sustainability labels by merchant")
    st.caption("Sustainability label credibility score >= 50 is credible and < 50 is not credible")
    st.plotly_chart(
        fetch_and_cache_product_count_by_sustainability_label_credibility(green_db)[
            "plot_product_count_w_credibility"
        ]
    )

    st.markdown("""---""")


def render_leaderboards(green_db: GreenDB) -> None:
    st.subheader("Rank by sustainability")
    st.caption(
        "Products ranked by aggregated mean sustainability score from unique and credible "
        "products in the database."
    )
    c1, c2, c3 = st.columns(3)
    c1.write("🌟 Rank per shop")
    c1.dataframe(fetch_and_cache_leaderboards(green_db)["rank_by_merchant"])
    c2.write("🌟 Rank per category")
    c2.dataframe(fetch_and_cache_leaderboards(green_db)["rank_by_category"])
    c3.write("🌟 Rank per brand")
    c3.dataframe(fetch_and_cache_leaderboards(green_db)["rank_by_brand"])


def render_credible_products_plots(green_db: GreenDB):
    st.subheader("Products with credible sustainability labels by category")
    fashion, electronics = st.tabs(["👗Fashion", "🔌Electronics"])

    fashion.plotly_chart(
        fetch_and_cache_product_count_credible_sustainability_labels_by_category(green_db)[
            "plot_product_count_credible_sustainability_labels_fashion"
        ],
        use_container_width=True,
    )
    electronics.plotly_chart(
        fetch_and_cache_product_count_credible_sustainability_labels_by_category(green_db)[
            "plot_product_count_credible_sustainability_labels_electronics"
        ],
        use_container_width=True,
    )

    st.subheader("Categories by ecological and social scores")
    st.session_state["product_family_selection"] = st.radio(
        label="Select product family:", options=["all", "electronics", "fashion"], horizontal=True
    )
    if st.session_state["product_family_selection"] == "all":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score(green_db)[
                "plot_credibility_and_sustainability_by_brand_all"
            ]
        )
    elif st.session_state["product_family_selection"] == "fashion":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score(green_db)[
                "plot_credibility_and_sustainability_by_brand_fashion"
            ]
        )
    elif st.session_state["product_family_selection"] == "electronics":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score(green_db)[
                "plot_credibility_and_sustainability_by_brand_electronics"
            ]
        )

    st.caption(
        "Figure shows aggregated ecological and social scores (from 0 to 100) by category for all "
        "unique and credible products in the database. The size of the bubble represents number of "
        "products per category."
    )


def main() -> None:
    st.set_page_config(page_title="Leaderboards", page_icon="♻️")
    with st.sidebar:
        render_sidebar_leaderboards(green_db)

    render_plots_product_count_by_credibility(green_db)
    render_leaderboards(green_db)
    render_credible_products_plots(green_db)


main()
