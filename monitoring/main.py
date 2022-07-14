import os
import sys
import datetime

import streamlit as st

#Streamlit is not aware of local modules
sys.path.append("/Users/adrsanchez/PycharmProjects/green-db/")
#Env variables
os.environ["POSTGRES_SCRAPING_USER"] = "scraping"
os.environ["POSTGRES_SCRAPING_PASSWORD"] = "scraping1992"
os.environ["POSTGRES_SCRAPING_HOST"] = "127.0.0.1"
os.environ["POSTGRES_SCRAPING_PORT"] = "5432"
os.environ["POSTGRES_GREEN_DB_USER"] = "green-db"
os.environ["POSTGRES_GREEN_DB_PASSWORD"] = "green1992"
os.environ["POSTGRES_GREEN_DB_HOST"] = "127.0.0.1"
os.environ["POSTGRES_GREEN_DB_PORT"] = "5432"

from database.database.connection import GreenDB
from monitoring.viz_utils import category_mosaic_chart, category_stack_bars, timeline
green_db = GreenDB()

#Starts visualization
st.title("GreenDB")
st.header("A Product-by-Product Sustainability Database")
st.subheader("Green-DB Summary")
h1, h2 = st.columns(2)
h1.write("Latest timestamp of data extraction:")
h2.write(green_db.get_latest_timestamp().date())

m1, m2, m3 = st.columns(3)
num_products = green_db.get_last_extraction_summary()
m1.metric(label="Number of products", value=num_products['products_extracted'].sum())
m2.metric(label="Number of categories", value=len(green_db.get_category_summary().groupby('category')))
m3.metric(label="Number of merchants", value=len(green_db.get_category_summary().groupby('merchant')))

st.write("Latest extraction by merchant")
st.dataframe(green_db.get_last_extraction_summary())

st.write("Categories by merchant")
st.caption("From latest products extraction")
st.plotly_chart(category_stack_bars(green_db.get_category_summary()), use_container_width=False)


st.write("Extraction all timestamps")
st.plotly_chart(timeline(green_db.get_timestamps_by_merchant()), use_container_width=True)


st.write("Extraction all timestamps by merchant")
all_timestamps_by_merchant = green_db.get_timestamps_by_merchant()
st.dataframe(all_timestamps_by_merchant)
