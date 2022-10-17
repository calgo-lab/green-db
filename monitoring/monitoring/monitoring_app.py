import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    render_basic_information,
    render_extended_information,
    render_leaderboards,
    render_sidebar,
    render_product_ranking,
)

green_db = GreenDB()


def main() -> None:
    """
    This represents the basic structure of the Monitoring App.
    """
    st.set_page_config(page_icon="♻️", page_title="GreenDB")
    st.title("GreenDB - A Product-by-Product Sustainability Database")

    # Sidebar with general overview of the project
    with st.sidebar:
        render_sidebar(green_db)

    basic_information_tab, extended_information_tab, leaderboards_tab, ranking_tab = st.tabs(
        ["Basic Information", "Extended Information (as Tables)", "Leaderboards", "Products "
                                                                                  "ranking"]
    )
    # Main tab with all plots
    with basic_information_tab:
        render_basic_information(green_db)

    # Secondary tab with dataframes
    with extended_information_tab:
        render_extended_information(green_db)

    # Leaderboards tab
    with leaderboards_tab:
        render_leaderboards(green_db)

    # Products ranking
    with ranking_tab:
        render_product_ranking(green_db)


main()
