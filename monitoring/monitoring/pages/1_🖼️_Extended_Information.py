import streamlit as st

from database.connection import GreenDB
from monitoring.utils import (
    render_extended_information,
)

green_db = GreenDB()

st.set_page_config(page_title="Extended Information", page_icon="♻️")
render_extended_information(green_db)
