import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    render_leaderboards,
    render_plots_product_count_by_credibility,
    render_sidebar_leaderboards,
)

green_db = GreenDB()

st.set_page_config(page_title="Leaderboards", page_icon="♻️")
with st.sidebar:
    render_sidebar_leaderboards(green_db)
render_plots_product_count_by_credibility(green_db)
render_leaderboards(green_db)
