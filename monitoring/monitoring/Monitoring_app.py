import streamlit as st

from database.connection import GreenDB
from monitoring.utils import render_basic_information, render_sidebar

green_db = GreenDB()

st.set_page_config(page_title="GreenDB", page_icon="♻️")
st.title("GreenDB - A Product-by-Product Sustainability Database")

# Sidebar with general overview of the project
with st.sidebar:
    render_sidebar(green_db)

render_basic_information(green_db)
