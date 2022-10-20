import streamlit as st

from database.connection import GreenDB
from monitoring.utils import render_product_ranking, render_product_ranking_filters_as_sidebar

green_db = GreenDB()

st.set_page_config(page_title="Product Ranking", page_icon="♻️")
with st.sidebar:
    render_product_ranking_filters_as_sidebar()
render_product_ranking(green_db)
