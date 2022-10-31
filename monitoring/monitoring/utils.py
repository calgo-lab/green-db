from typing import Any, Callable

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from core.constants import ALL_SCRAPING_TABLE_NAMES
from database.connection import GreenDB, Scraping
from database.tables import SustainabilityLabelsTable


@st.experimental_singleton
def hash_greendb() -> Callable[[], Any]:
    """
    Helper function to hash connection to the database.

    Returns:
          Hashed `Connection` for the GreenDB.
    """
    return GreenDB()


@st.experimental_memo(ttl=604800)
def fetch_and_cache_scraped_page_and_product_count_per_merchant_and_country(
    _green_db: Callable[[], Any] = hash_greendb
) -> dict:
    """
    Fetch product count and scraped pages per merchant and country for all timestamps. Save
        objects in streamlit cache: pd.DataFrame with queried data and linear plotly
        charts for scraped pages vs extracted product over timestamp and over timestamp per
        merchant.

    Args:
        green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    # Fetch and save DataFrame
    data_frame_product_count_per_merchant_and_country = (
        _green_db.get_product_count_per_merchant_and_country()  # type: ignore[attr-defined] # noqa
    )
    data_frame_product_count_per_merchant_and_country["type"] = "extract"

    data_frame_scraped_page_count_per_merchant_and_country = pd.concat(
        [
            Scraping(table_name).get_scraped_page_count_per_merchant_and_country()
            for table_name in ALL_SCRAPING_TABLE_NAMES
        ]
    ).rename(columns={"scraped_page_count": "product_count"})
    data_frame_scraped_page_count_per_merchant_and_country["type"] = "scraping"

    data_frame_scraped_page_and_product_count_per_merchant_and_country = pd.concat(
        [
            data_frame_scraped_page_count_per_merchant_and_country,
            data_frame_product_count_per_merchant_and_country,
        ],
        ignore_index=True,
    )

    return {
        "data_frame": data_frame_scraped_page_and_product_count_per_merchant_and_country,
        "plot_scraped_vs_extracted_over_timestamp": px.line(
            data_frame_scraped_page_and_product_count_per_merchant_and_country.groupby(
                by=["timestamp", "type"]
            )
            .sum()
            .reset_index(),
            x="timestamp",
            y="product_count",
            color="type",
        ),
        "pivot_scraped_vs_extracted": (
            data_frame_scraped_page_and_product_count_per_merchant_and_country.pivot_table(
                values="product_count",
                index=["timestamp", "merchant", "country"],
                columns="type",
                aggfunc=sum,
                fill_value=0,
            )
        ),
        "latest_sustainability_labels_timestamp": _green_db.get_latest_timestamp(  # type: ignore[attr-defined] # noqa
            SustainabilityLabelsTable
        ).date(),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_latest_product_count_per_merchant_and_country(
    _green_db: Callable[[], Any] = hash_greendb
) -> dict:
    """
    Fetch product count per merchant and country for latest timestamp available. Saves total number
        of extracted products and total number of unique merchants in streamlit cache.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    # Fetch and save DataFrame
    data_frame_latest_product_count_per_merchant_and_country = (
        _green_db.get_latest_product_count_per_merchant_and_country()  # type: ignore[attr-defined] # noqa
    )
    # and calculate some values for convenience
    return {
        "latest_extraction_timestamp": _green_db.get_latest_timestamp().date(),  # type: ignore[attr-defined] # noqa
        "latest_extraction_number_of_products": data_frame_latest_product_count_per_merchant_and_country[
            "product_count"
        ].sum(),
        "latest_extraction_number_of_merchants": len(
            data_frame_latest_product_count_per_merchant_and_country.groupby("merchant")
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_latest_scraped_page_count_per_merchant_and_country() -> dict:
    """
    Fetch scraped pages per merchant and country for latest timestamp available. Saves a
        pd.DataFrame with queried data for all tables in ScrapingDB and total number of scraped
        pages in streamlit cache.

    Args:
        green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    # Fetch and save DataFrame
    data_frame_latest_scraped_page_count_per_merchant_and_country = pd.concat(
        [
            Scraping(table_name).get_latest_scraped_page_count_per_merchant_and_country()
            for table_name in ALL_SCRAPING_TABLE_NAMES
        ]
    )
    # and calculate some values for convenience
    return {
        "latest_scraping_number_of_scraped_pages": data_frame_latest_scraped_page_count_per_merchant_and_country[
            "scraped_page_count"
        ].sum(),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_latest_product_count_per_category_and_merchant(
    _green_db: Callable[[], Any] = hash_greendb,
) -> dict:
    """
    Fetch product count per category per merchant for latest timestamp available. Save objects
        in streamlit cache: pd.DataFrame with queried data, total number of categories and bar
        plot for fetched data.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

     Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    data_frame_latest_product_count_per_category_and_merchant = (
        _green_db.get_latest_product_count_per_category_and_merchant()  # type: ignore[attr-defined] # noqa
    )
    return {
        "data_frame": data_frame_latest_product_count_per_category_and_merchant,
        "latest_extraction_number_of_categories": len(
            data_frame_latest_product_count_per_category_and_merchant.groupby("category")
        ),
        "plot_latest_products_per_category_and_merchant": px.bar(
            data_frame_latest_product_count_per_category_and_merchant,
            x="category",
            y="product_count",
            color="merchant",
            text="product_count",
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_product_count_with_unknown_sustainability_label(
    _green_db: Callable[[], Any] = hash_greendb,
) -> dict:
    """
    Fetch product count for products with unknown sustainability label(s). Saves a pd.DataFrame and
         a line plot from queried data in streamlit cache.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    data_frame_product_count_with_unknown_sustainability_label = (
        _green_db.get_product_count_with_unknown_sustainability_label()  # type: ignore[attr-defined] # noqa
    )
    return {
        "data_frame": data_frame_product_count_with_unknown_sustainability_label,
        "plot": px.line(
            data_frame_product_count_with_unknown_sustainability_label,
            x="timestamp",
            y="product_count",
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_product_count_by_sustainability_label_credibility_overtime(
    _green_db: Callable[[], Any] = hash_greendb,
) -> dict:
    """
    Fetch product count for products by sustainability label credibility grouped in: all
        extracted, certificate:OTHER and credible. Saves a line plot from queried data in streamlit
        cache.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    return (
        alt.Chart(_green_db.get_product_count_by_sustainability_label_credibility_all_timestamps())  # type: ignore[attr-defined] # noqa
        .mark_line()
        .encode(
            x="timestamp", y=alt.Y("product_count", stack=None), color="merchant", strokeDash="type"
        )
    )


@st.experimental_memo(ttl=604800)
def fetch_and_cache_extended_information(_green_db: Callable[[], Any] = hash_greendb) -> dict:
    """
    Fetch product count by sustainability label and list of products with unknown sustainability
        labels from latest timestamp available.

    Args:
       _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached dataframes to render in streamlit.
    """
    return {
        "latest_product_count_per_sustainability_label": (
            _green_db.get_latest_product_count_per_sustainability_label()  # type: ignore[attr-defined] # noqa
        ),
        "latest_products_with_unknown_sustainability_label": (
            _green_db.get_latest_products_with_unknown_sustainability_label()  # type: ignore[attr-defined] # noqa
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_product_count_by_sustainability_label_credibility(
    _green_db: Callable[[], Any] = hash_greendb,
) -> dict:
    """
    Fetch product count by sustainability label's credibility from all unique products in the
        database. Saves in cache: total number of unique products, total number of unique products
        with credibility, a normalized bar plot of products sustainability label's credibility by
        merchant and a pie chart of products with credibility by merchant.

    Args:
        green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    data_frame_product_count_by_sustainability_label_credibility = (
        _green_db.get_product_count_by_sustainability_label_credibility()  # type: ignore[attr-defined] # noqa
    )
    return {
        "all_unique_product_count": data_frame_product_count_by_sustainability_label_credibility[
            "product_count"
        ].sum(),
        "unique_credible_product_count": data_frame_product_count_by_sustainability_label_credibility[
            data_frame_product_count_by_sustainability_label_credibility.type == "credible"
        ][
            "product_count"
        ].sum(),
        "unique_credible_product_count_by_merchant": data_frame_product_count_by_sustainability_label_credibility.groupby(
            ["merchant"]
        )
        .sum()
        .sort_values(by="product_count", ascending=False),
        "plot_normalized_product_count_w_vs_wo_credibility": (
            alt.Chart(data_frame_product_count_by_sustainability_label_credibility)
            .mark_bar()
            .encode(
                x=alt.X("sum(product_count)", stack="normalize"),
                y=alt.Y("merchant", sort="-x"),
                color="type",
            )
        ),
        "plot_product_count_w_credibility": px.pie(
            data_frame_product_count_by_sustainability_label_credibility[
                data_frame_product_count_by_sustainability_label_credibility.type == "credible"
            ],
            values="product_count",
            names="merchant",
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_leaderboards(_green_db: Callable[[], Any] = hash_greendb) -> dict:
    """
    Saves in streamlit cache ranking by sustainability at merchant, category and brand level.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached dataframes to render in streamlit.
    """
    return {
        "rank_by_merchant": _green_db.get_rank_by_sustainability("merchant"),  # type: ignore[attr-defined] # noqa
        "rank_by_category": _green_db.get_rank_by_sustainability("category"),  # type: ignore[attr-defined] # noqa
        "rank_by_brand": _green_db.get_rank_by_sustainability("brand"),  # type: ignore[attr-defined] # noqa
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_product_families(_green_db: Callable[[], Any] = hash_greendb) -> dict:
    """
    Fetch and saves categories grouped by family.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached list of categories.
    """
    all_categories = list(
        _green_db.get_product_count_by_sustainability_label_and_category()["category"].unique()  # type: ignore[attr-defined] # noqa
    )
    electronics_categories = [
        "PRINTER",
        "LAPTOP",
        "TABLET",
        "DISHWASHER",
        "FRIDGE",
        "OVEN",
        "COOKER_HOOD",
        "FREEZER",
        "WASHER",
        "DRYER",
    ]
    return {
        "all_categories": all_categories,
        "electronics": electronics_categories,
        "fashion": [
            category for category in all_categories if category not in electronics_categories
        ],
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_product_count_credible_sustainability_labels_by_category(
    _green_db: Callable[[], Any] = hash_greendb,
) -> dict:
    """
    Fetch and saves product count by sustainability label and category from all unique products
        with credibility in the database. Creates two bar plots with this data for electronics and
        fashion categories.

    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    data_frame_product_count_credible_sustainability_labels_by_category = (
        _green_db.get_product_count_by_sustainability_label_and_category()  # type: ignore[attr-defined] # noqa
    )
    return {
        "plot_product_count_credible_sustainability_labels_fashion": px.bar(
            data_frame_product_count_credible_sustainability_labels_by_category[
                data_frame_product_count_credible_sustainability_labels_by_category.category.isin(
                    fetch_and_cache_product_families(_green_db)["fashion"]
                )
            ].sort_values(by="product_count"),
            x="product_count",
            y="category",
            color="sustainability_label",
        ),
        "plot_product_count_credible_sustainability_labels_electronics": px.bar(
            data_frame_product_count_credible_sustainability_labels_by_category[
                data_frame_product_count_credible_sustainability_labels_by_category.category.isin(
                    fetch_and_cache_product_families(_green_db)["electronics"]
                )
            ].sort_values(by="product_count"),
            x="product_count",
            y="category",
            color="sustainability_label",
        ),
    }


@st.experimental_memo(ttl=604800)
def fetch_and_cache_category_ecological_vs_social_score_by_category(
    _green_db: Callable[[], Any] = hash_greendb
) -> dict:
    """
    Fetch and saves aggregated ecological and social scores by category. Saves three scatter
        plots in cache for this data per category family (all, electronics and
        fashion)
    Args:
        _green_db (hash_greendb): `Connection` for the GreenDB.

    Returns:
        dict: Dictionary containing cached objects to render in streamlit.
    """
    data_frame_credibility_and_sustainability_by_category = (
        _green_db.get_credibility_and_sustainability_scores_by_category()  # type: ignore[attr-defined] # noqa
    )

    return {
        "plot_ecological_vs_social_score_all_categories": px.scatter(
            data_frame_credibility_and_sustainability_by_category,
            x="ecological_score",
            y="social_score",
            size="product_count",
            color="category",
        ),
        "plot_ecological_vs_social_score_fashion_categories": px.scatter(
            (
                data_frame_credibility_and_sustainability_by_category[
                    data_frame_credibility_and_sustainability_by_category.category.isin(
                        fetch_and_cache_product_families(_green_db)["fashion"]
                    )
                ]
            ),
            x="ecological_score",
            y="social_score",
            size="product_count",
            color="category",
        ),
        "plot_ecological_vs_social_score_electronics_categories": px.scatter(
            (
                data_frame_credibility_and_sustainability_by_category[
                    data_frame_credibility_and_sustainability_by_category.category.isin(
                        fetch_and_cache_product_families(_green_db)["electronics"]
                    )
                ]
            ),
            x="ecological_score",
            y="social_score",
            size="product_count",
            color="category",
        ),
    }
