import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    clear_cache,
    latest_cached_timestamp,
    render_credible_products_plots,
    render_leaderboards,
    render_plots_product_count_by_credibility,
    render_sidebar_leaderboards,
)

green_db = GreenDB()

st.set_page_config(page_title="Leaderboards", page_icon="♻️")

clear_cache(green_db)
with st.sidebar:
    render_sidebar_leaderboards(green_db)
render_plots_product_count_by_credibility(green_db)
render_leaderboards(green_db)
render_credible_products_plots(green_db)
latest_cached_timestamp(green_db)
