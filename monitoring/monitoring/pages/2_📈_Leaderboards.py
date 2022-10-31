import streamlit as st

from monitoring.utils import (
    fetch_and_cache_category_ecological_vs_social_score_by_category,
    fetch_and_cache_leaderboards,
    fetch_and_cache_product_count_by_sustainability_label_credibility,
    fetch_and_cache_product_count_credible_sustainability_labels_by_category,
    hash_greendb,
)


def render_sidebar_leaderboards() -> None:
    """
    Render streamlit sidebar from previously initialized cache to show an introduction to the
        page with number of unique products and unique products with credible sustainability
        label(s) in the database.
    """
    st.write(
        "All unique products",
        fetch_and_cache_product_count_by_sustainability_label_credibility(hash_greendb())[
            "all_unique_product_count"
        ],
    )
    st.write(
        "Unique products with credibility",
        fetch_and_cache_product_count_by_sustainability_label_credibility(hash_greendb())[
            "unique_credible_product_count"
        ],
    )
    st.write("All unique products by merchant")
    st.dataframe(
        fetch_and_cache_product_count_by_sustainability_label_credibility(hash_greendb())[
            "unique_credible_product_count_by_merchant"
        ]
    )


def render_plots_product_count_by_credibility() -> None:
    """
    This section renders cached visualizations for products by its sustainability label
    credibility.
    """
    st.header("GreenDB Leaderboards")
    st.subheader("Product credibility by merchant")
    st.caption(
        "Calculated from all unique products in the database. Where "
        "sustainability label credibility score >= 50 is credible and < 50 is not credible."
    )
    st.altair_chart(
        fetch_and_cache_product_count_by_sustainability_label_credibility(hash_greendb())[
            "plot_normalized_product_count_w_vs_wo_credibility"
        ],
        use_container_width=True,
    )

    st.subheader("Product with credible sustainability labels by merchant")
    st.caption("Sustainability label credibility score >= 50 is credible and < 50 is not credible")
    st.plotly_chart(
        fetch_and_cache_product_count_by_sustainability_label_credibility(hash_greendb())[
            "plot_product_count_w_credibility"
        ]
    )

    st.markdown("""---""")


def render_leaderboards() -> None:
    """
    This section renders leaderboards at merchant, category and brand level. Ranked by
        aggregated mean sustainability score.
    """
    st.subheader("Rank by sustainability")
    st.caption(
        "Products ranked by aggregated mean sustainability score from unique and credible "
        "products in the database."
    )
    c1, c2, c3 = st.columns(3)
    c1.write("🌟 Rank per shop")
    c1.dataframe(fetch_and_cache_leaderboards(hash_greendb())["rank_by_merchant"])
    c2.write("🌟 Rank per category")
    c2.dataframe(fetch_and_cache_leaderboards(hash_greendb())["rank_by_category"])
    c3.write("🌟 Rank per brand")
    c3.dataframe(fetch_and_cache_leaderboards(hash_greendb())["rank_by_brand"])


def render_credible_products_plots():
    """
    This method renders cached plots for all unique products with credibility in the database.
        Render a bar plot to show sustainability labels distribution by category and a scatter plot
        that shows categories' ecological and social scores. Both visualization can be filtered by
        category family.
    """
    st.subheader("Products with credible sustainability labels by category")
    fashion, electronics = st.tabs(["👗Fashion", "🔌Electronics"])

    fashion.plotly_chart(
        fetch_and_cache_product_count_credible_sustainability_labels_by_category(hash_greendb())[
            "plot_product_count_credible_sustainability_labels_fashion"
        ],
        use_container_width=True,
    )
    electronics.plotly_chart(
        fetch_and_cache_product_count_credible_sustainability_labels_by_category(hash_greendb())[
            "plot_product_count_credible_sustainability_labels_electronics"
        ],
        use_container_width=True,
    )

    st.subheader("Categories by ecological and social scores")
    st.caption(
        "Figure shows aggregated ecological and social scores (from 0 to 100) by category for all "
        "unique and credible products in the database. The size of the bubble represents number of "
        "products per category."
    )
    st.session_state["product_family_selection"] = st.radio(
        label="Select product family:", options=["all", "electronics", "fashion"], horizontal=True
    )
    if st.session_state["product_family_selection"] == "all":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score_by_category(hash_greendb())[
                "plot_ecological_vs_social_score_all_categories"
            ]
        )
    elif st.session_state["product_family_selection"] == "fashion":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score_by_category(hash_greendb())[
                "plot_ecological_vs_social_score_fashion_categories"
            ]
        )
    elif st.session_state["product_family_selection"] == "electronics":
        st.plotly_chart(
            fetch_and_cache_category_ecological_vs_social_score_by_category(hash_greendb())[
                "plot_ecological_vs_social_score_electronics_categories"
            ]
        )


def main() -> None:
    """
    This represents the basic structure of the Leaderboards page.
    """
    st.set_page_config(page_title="Leaderboards", page_icon="♻️")
    with st.sidebar:
        render_sidebar_leaderboards()

    render_plots_product_count_by_credibility()
    render_leaderboards()
    render_credible_products_plots()


main()
