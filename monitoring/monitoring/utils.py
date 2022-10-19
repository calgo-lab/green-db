import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import GreenDB, Scraping
from database.tables import SustainabilityLabelsTable



def fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(
    green_db: GreenDB,
) -> None:
    """
    Fetch product count and scraped pages per merchant and country for all timestamps. Save
        objects in streamlit cache: pd.DataFrame with queried data and linear plotly
        charts for scraped pages vs extracted product over timestamp and over timestamp per
        merchant.


    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_scraped_page_and_product_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_product_count_per_merchant_and_country"
        ] = green_db.get_product_count_per_merchant_and_country()
        st.session_state["data_frame_product_count_per_merchant_and_country"]["type"] = "extract"

        st.session_state["data_frame_scraped_page_count_per_merchant_and_country"] = pd.concat(
            [
                Scraping(table_name).get_scraped_page_count_per_merchant_and_country()
                for table_name in ALL_SCRAPING_TABLE_NAMES
            ]
        ).rename(columns={"scraped_page_count": "product_count"})
        st.session_state["data_frame_scraped_page_count_per_merchant_and_country"][
            "type"
        ] = "scraping"

        st.session_state[
            "data_frame_scraped_page_and_product_count_per_merchant_and_country"
        ] = pd.concat(
            [
                st.session_state["data_frame_scraped_page_count_per_merchant_and_country"],
                st.session_state["data_frame_product_count_per_merchant_and_country"],
            ],
            ignore_index=True,
        )

        # Plot and restructure the dataframe
        st.session_state["plot_scraped_vs_extracted_over_timestamp_per_merchant"] = px.line(
            st.session_state["data_frame_scraped_page_and_product_count_per_merchant_and_country"]
            .groupby(by=["timestamp", "merchant", "type"])
            .sum()
            .reset_index(),
            x="timestamp",
            y="product_count",
            color="merchant",
            symbol="type",
        )
        st.session_state["plot_scraped_vs_extracted_over_timestamp"] = px.line(
            st.session_state["data_frame_scraped_page_and_product_count_per_merchant_and_country"]
            .groupby(by=["timestamp", "type"])
            .sum()
            .reset_index(),
            x="timestamp",
            y="product_count",
            color="type",
        )
        st.session_state["pivot_scraped_vs_extracted"] = st.session_state[
            "data_frame_scraped_page_and_product_count_per_merchant_and_country"
        ].pivot_table(
            values="product_count",
            index=["timestamp", "merchant", "country"],
            columns="type",
            aggfunc=sum,
            fill_value=0,
        )



def fetch_and_cache_latest_product_count_per_merchant_and_country(green_db: GreenDB) -> None:
    """
    Fetch product count per merchant and country for latest timestamp available. Saves a
        pd.DataFrame with queried data, total number of extracted products and total number of
        unique merchants in streamlit cache.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_latest_product_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_latest_product_count_per_merchant_and_country"
        ] = green_db.get_latest_product_count_per_merchant_and_country()

        # and calculate some values for convenience
        st.session_state["latest_extraction_number_of_products"] = st.session_state[
            "data_frame_latest_product_count_per_merchant_and_country"
        ]["product_count"].sum()
        st.session_state["latest_extraction_number_of_merchants"] = len(
            st.session_state["data_frame_latest_product_count_per_merchant_and_country"].groupby(
                "merchant"
            )
        )



def fetch_and_cache_latest_scraped_page_count_per_merchant_and_country() -> None:
    """
    Fetch scraped pages per merchant and country for latest timestamp available. Saves a
        pd.DataFrame with queried data for all tables in ScrapingDB and total number of scraped
        pages in streamlit cache.
    """
    if "data_frame_latest_scraped_page_count_per_merchant_and_country" not in st.session_state:

        # Fetch and save DataFrame
        st.session_state[
            "data_frame_latest_scraped_page_count_per_merchant_and_country"
        ] = pd.concat(
            [
                Scraping(table_name).get_latest_scraped_page_count_per_merchant_and_country()
                for table_name in ALL_SCRAPING_TABLE_NAMES
            ]
        )

        # and calculate some values for convenience
        st.session_state["latest_scraping_number_of_scraped_pages"] = st.session_state[
            "data_frame_latest_scraped_page_count_per_merchant_and_country"
        ]["scraped_page_count"].sum()



def fetch_and_cache_latest_product_count_per_category_and_merchant(green_db: GreenDB) -> None:
    """
    Fetch product count per category per merchant for latest timestamp available. Save objects
        in streamlit cache: pd.DataFrame with queried data, total number of categories and bar
        plot for fetched data.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_latest_product_count_per_category_and_merchant" not in st.session_state:
        st.session_state[
            "data_frame_latest_product_count_per_category_and_merchant"
        ] = green_db.get_latest_product_count_per_category_and_merchant()

        st.session_state["latest_extraction_number_of_categories"] = len(
            st.session_state["data_frame_latest_product_count_per_category_and_merchant"].groupby(
                "category"
            )
        )

        st.session_state["plot_latest_products_per_category_and_merchant"] = px.bar(
            st.session_state["data_frame_latest_product_count_per_category_and_merchant"],
            x="category",
            y="product_count",
            color="merchant",
            text="product_count",
        )



def fetch_and_cache_product_count_with_unknown_sustainability_label(green_db: GreenDB) -> None:
    """
    Fetch product count for products with unknown sustainability label(s). Saves a pd.DataFrame and
         a line plot from queried data in streamlit cache.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if "data_frame_product_count_with_unknown_sustainability_label" not in st.session_state:
        st.session_state[
            "data_frame_product_count_with_unknown_sustainability_label"
        ] = green_db.get_product_count_with_unknown_sustainability_label()

        st.session_state["plot_product_count_with_unknown_sustainability_label"] = px.line(
            st.session_state["data_frame_product_count_with_unknown_sustainability_label"],
            x="timestamp",
            y="product_count",
        )


def render_sidebar(green_db: GreenDB) -> None:
    """
    Render streamlit sidebar from previously initialized session states. Sidebar provides a
        quick overview of the latest data extraction.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    st.title("Overview")
    st.write("From last data extraction on:")
    st.write(green_db.get_latest_timestamp().date())

    fetch_and_cache_latest_scraped_page_count_per_merchant_and_country()
    st.metric(
        label="Number scraped pages",
        value=st.session_state["latest_scraping_number_of_scraped_pages"],
    )

    fetch_and_cache_latest_product_count_per_merchant_and_country(green_db)
    st.metric(
        label="Number extracted products",
        value=st.session_state["latest_extraction_number_of_products"],
    )

    fetch_and_cache_latest_product_count_per_category_and_merchant(green_db)
    st.metric(
        label="Number of categories",
        value=st.session_state["latest_extraction_number_of_categories"],
    )

    st.metric(
        label="Number of merchants",
        value=st.session_state["latest_extraction_number_of_merchants"],
    )

    st.write("Sustainability label's last update:")
    st.write(green_db.get_latest_timestamp(SustainabilityLabelsTable).date())


def render_basic_information(green_db: GreenDB) -> None:
    """
    Render 'basic information' from previously initialized session states in streamlit. This is
        the main tab of the report, includes all plots.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(green_db)
    st.subheader("Scraped pages and extracted products")
    st.plotly_chart(st.session_state["plot_scraped_vs_extracted_over_timestamp"])

    st.markdown("""---""")

    st.subheader("Scraped pages and extracted products by merchants")
    st.plotly_chart(st.session_state["plot_scraped_vs_extracted_over_timestamp_per_merchant"])

    st.markdown("""---""")

    st.subheader("Latest products per category and merchant")
    st.plotly_chart(st.session_state["plot_latest_products_per_category_and_merchant"])

    st.markdown("""---""")

    fetch_and_cache_product_count_with_unknown_sustainability_label(green_db)
    st.subheader("Products with UNKNOWN sustainability label")
    st.plotly_chart(st.session_state["plot_product_count_with_unknown_sustainability_label"])


def render_extended_information(green_db: GreenDB) -> None:
    """
    Render dataframes from session states in streamlit just when user clicks to fetch the data.
        This is the secondary tab of the report.

    Args:
        green_db (GreenDB): `Connection` for the GreenDB.
    """
    if st.button("Do you want to fetch this data? - Could take a while."):

        st.subheader("Scraped pages vs. extracted products count as table")
        st.dataframe(st.session_state["pivot_scraped_vs_extracted"])

        st.markdown("""---""")

        st.subheader("Latest product count by sustainability label as table")
        if "latest_product_count_per_sustainability_label" not in st.session_state:
            st.session_state.latest_product_count_per_sustainability_label = (
                green_db.get_latest_product_count_per_sustainability_label()
            )
        st.write(
            "Number of sustainability labels in use:",
            len(st.session_state.latest_product_count_per_sustainability_label),
        )
        st.dataframe(st.session_state.latest_product_count_per_sustainability_label)

        st.markdown("""---""")

        st.subheader("Latest products with UNKNOWN label as table")
        if "latest_products_with_unknown_sustainability_label" not in st.session_state:
            st.session_state.latest_products_with_unknown_sustainability_label = (
                green_db.get_latest_products_with_unknown_sustainability_label()
            )
        st.dataframe(st.session_state.latest_products_with_unknown_sustainability_label)


def fetch_and_cache_product_count_credible_vs_not_credible_sustainability_labels(green_db: GreenDB):
    if "plot_normalized_product_count_w_vs_wo_credibility" not in st.session_state:
        st.session_state["plot_normalized_product_count_w_vs_wo_credibility"] = (
            alt.Chart(green_db.get_product_count_credible_vs_not_credible_sustainability_labels())
            .mark_bar()
            .encode(
                x=alt.X("sum(product_count)", stack="normalize"),
                y=alt.Y("merchant", sort="-x"),
                color="type",
            )
        )
    if "data_frame_product_count_w_credibility" not in st.session_state:
        st.session_state[
            "data_frame_product_count_w_credibility"
        ] = green_db.get_product_count_credible_vs_not_credible_sustainability_labels()

    if "plot_product_count_w_credibility" not in st.session_state:
        st.session_state["plot_product_count_w_credibility"] = px.pie(
            st.session_state["data_frame_product_count_w_credibility"][
                st.session_state["data_frame_product_count_w_credibility"].type == "credible"
            ],
            values="product_count",
            names="merchant",
        )


def fetch_and_cache_product_count_credible_sustainability_labels_by_category(green_db: GreenDB):
    if "data_frame_product_count_credible_sustainability_labels" not in st.session_state:
        st.session_state[
            "data_frame_product_count_credible_sustainability_labels"
        ] = green_db.get_product_count_by_label_and_category()

    if "plot_product_count_credible_sustainability_labels_fashion" not in st.session_state:
        st.session_state["plot_product_count_credible_sustainability_labels_fashion"] = px.bar(
            st.session_state["data_frame_product_count_credible_sustainability_labels"][
                ~st.session_state["data_frame_product_count_credible_sustainability_labels"][
                    "sustainability_label"
                ].str.contains("EU Energielabel")
            ].sort_values(by="product_count"),
            x="product_count",
            y="category",
            color="sustainability_label",
        )

    if "plot_product_count_credible_sustainability_labels_electronics" not in st.session_state:
        st.session_state["plot_product_count_credible_sustainability_labels_electronics"] = px.bar(
            st.session_state["data_frame_product_count_credible_sustainability_labels"][
                st.session_state["data_frame_product_count_credible_sustainability_labels"][
                    "sustainability_label"
                ].str.contains("EU Energielabel")
            ],
            x="product_count",
            y="category",
            color="sustainability_label",
        )

def render_sidebar_leaderboards(green_db: GreenDB) -> None:
    st.write("All unique products by merchant")
    st.dataframe(green_db.get_product_count_credible_vs_not_credible_sustainability_labels().groupby(["merchant"]).sum())
    st.write("All unique products", green_db.scores()[0])
    st.write("Unique products with credibility", green_db.scores()[1])

def render_leaderboards(green_db: GreenDB) -> None:
    fetch_and_cache_product_count_credible_vs_not_credible_sustainability_labels(green_db)
    st.header("GreenDB Leaderboards")
    st.subheader("Product credibility by merchant")
    st.caption(
        "Calculated from all unique products in the database. Where "
        "sustainability label credibility score >= 50 is credible and < 50 is not credible."
    )
    st.altair_chart(
        st.session_state["plot_normalized_product_count_w_vs_wo_credibility"],
        use_container_width=True,
    )

    st.subheader("Product with credible sustainability labels by merchant")
    st.caption("Sustainability label credibility score >= 50 is credible and < 50 is not credible")
    st.plotly_chart(st.session_state["plot_product_count_w_credibility"])

    st.markdown("""---""")

    st.subheader("Rank by credibility")
    st.caption(
        "Based on aggregated mean credibility from ALL unique products in the database "
        "with credibility score. Products with NULL credibility has been excluded from "
        "calculation."
    )
    c1, c2, c3 = st.columns(3)
    c1.write("🌟 Rank per shop")
    if "data_frame_credibility_by_merchant" not in st.session_state:
        st.session_state.data_frame_credibility_by_merchant = green_db.get_rank_by_credibility(
            "merchant"
        )
    c1.dataframe(st.session_state.data_frame_credibility_by_merchant)
    st.session_state.all_merchants = st.session_state.data_frame_credibility_by_merchant[
        "merchant"
    ].unique()
    c2.write("🌟 Rank per category")
    if "data_frame_credibility_by_category" not in st.session_state:
        st.session_state.data_frame_credibility_by_category = green_db.get_rank_by_credibility(
            "category"
        )
    c2.dataframe(st.session_state.data_frame_credibility_by_category)
    c3.write("🌟 Rank per brand")
    if "data_frame_credibility_by_brand" not in st.session_state:
        st.session_state["data_frame_credibility_by_brand"] = green_db.get_rank_by_credibility(
            "brand"
        )
    c3.dataframe(st.session_state.data_frame_credibility_by_brand)

    st.markdown("""---""")

    fetch_and_cache_product_count_credible_sustainability_labels_by_category(green_db)
    st.subheader("Products with credible sustainability labels by category")
    fashion, electronics = st.tabs(["👗Fashion", "🔌Electronics"])
    fashion.plotly_chart(
        st.session_state["plot_product_count_credible_sustainability_labels_fashion"],
        use_container_width=True,
    )
    electronics.plotly_chart(
        st.session_state["plot_product_count_credible_sustainability_labels_electronics"],
        use_container_width=True,
    )

    st.subheader("Brands credibility and sustainability scores")
    st.caption("From all unique products in the database with credible sustainability labels.")
    st.session_state["product_family_selection"] = st.radio(
        label="Select product family:", options=["all", "electronics", "fashion"], horizontal=True
    )
    if "data_frame_credibility_and_sustainability_by_brand" not in st.session_state:
        st.session_state[
            "data_frame_credibility_and_sustainability_by_brand"
        ] = green_db.get_scores_by_brand()
    if st.session_state["product_family_selection"] != "all":
        df_to_plot = st.session_state["data_frame_credibility_and_sustainability_by_brand"][
            st.session_state["data_frame_credibility_and_sustainability_by_brand"].product_family
            == st.session_state["product_family_selection"]
        ]
    else:
        df_to_plot = st.session_state["data_frame_credibility_and_sustainability_by_brand"]

    st.plotly_chart(
        px.scatter(
            (df_to_plot.sort_values(by="brand")),
            x="sustainability_score",
            y="mean_credibility",
            size="product_count",
            color="brand",
        )
    )


def render_product_ranking_filters_as_sidebar() -> None:
    product_family_filter = st.radio(
        label="Select product family:", options=["all", "electronics", "fashion"]
    )
    st.session_state["product_family_filter"] = product_family_filter

    number_of_products_to_fetch = st.number_input(
        "Choose number of products to fetch (max " "10k)", 10, 10000, 50
    )
    st.session_state["number_of_products_to_fetch"] = number_of_products_to_fetch

    merchants = list(
        st.session_state["data_frame_scraped_page_and_product_count_per_merchant_and_country"][
            "merchant"
        ].unique()
    )
    merchant_filter = st.multiselect(
        label="Filter by merchant", options=merchants, default=merchants[:]
    )
    st.session_state["merchant_filter"] = merchant_filter


def render_product_ranking(green_db: GreenDB) -> None:
    st.subheader("Top sustainable products in GreenDB")
    st.caption("From all unique products in the database with credible sustainability labels.")
    # TODO Update the category field while family product gets updated.
    categories = list(
        st.session_state["data_frame_latest_product_count_per_category_and_merchant"][
            "category"
        ].unique()
    )
    category_filter = st.multiselect(
        label="Filter by category", options=categories, default=categories[:]
    )
    st.session_state["category_filter"] = category_filter

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
            st.session_state["product_family_filter"],
            st.session_state["number_of_products_to_fetch"],
            st.session_state["rank_by"],
        )
        st.dataframe(data_frame_top_products)

        st.download_button(
            label="Download product sample CSV",
            data=data_frame_top_products.to_csv().encode("utf-8"),
            file_name="green_db_sample.csv",
            mime="text/csv",
        )
