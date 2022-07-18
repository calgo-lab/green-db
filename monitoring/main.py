import os
import sys
import pandas as pd
import streamlit as st
import collections
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
from workers.workers import CONNECTION_FOR_TABLE
from database.database.connection import GreenDB
green_db = GreenDB()

st.set_page_config(page_icon="♻️", page_title="GreenDB")

def category_stack_bars(df):
    fig = px.bar(df, x="category", y='products', color ='merchant', text='products')
    return (fig)


last_extraction_all = pd.DataFrame(green_db.get_last_job_summary(), columns=["country", "merchant", "timestamp", "products"]).sort_values(by="country")
extraction_all = pd.DataFrame(green_db.get_timestamps_by_merchant(), columns=["country", "merchant", "timestamp", "products"]).sort_values(by="country")
extraction_all['type'] = 'extraction'
last_scraping_all = pd.DataFrame([(CONNECTION_FOR_TABLE[table_name].get_last_job_summary()[0]) for table_name in CONNECTION_FOR_TABLE], columns=["country", "merchant", "timestamp", "products"]).sort_values(by="country")
scraping_all = pd.DataFrame([(CONNECTION_FOR_TABLE[table_name].get_timestamps_by_merchant()[0]) for table_name in CONNECTION_FOR_TABLE], columns=["country", "merchant", "timestamp", "products"]).sort_values(by="country")
scraping_all['type'] = 'scraping'
print(len(scraping_all))
all = pd.concat([extraction_all, scraping_all], ignore_index=True)
all['date'] = pd.to_datetime(all['timestamp']).dt.date
print(all)
all_pivot = all.pivot_table(values='products', index=['date', 'country','merchant'], columns=['type'], aggfunc=np.sum, fill_value=0)
print(all_pivot)
all_summ= all.pivot_table(values='products', index=['date'], columns='type', aggfunc=np.sum, fill_value=0)

print(all_summ)

def timeline():
    timestamps = all_summ.index
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=timestamps,
        y=all_summ['extraction'],
        name='Extraction',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=timestamps,
        y=all_summ['scraping'],
        name='Scraping',
        marker_color='lightsalmon'
    ))
    return fig


query = green_db.products_by_label()
freq = pd.DataFrame.from_dict((collections.Counter([label for row in query for label in row])), orient='index', columns=['products'])

#Starts visualization
st.title("GreenDB")
st.header("A Product-by-Product Sustainability Database")
st.subheader("Green-DB Summary")
h1, h2 = st.columns(2)
h1.write("Latest timestamp of data extraction:")
h2.write(green_db.get_latest_timestamp().date())

m1, m2, m3 = st.columns(3)

m1.metric(label="Number extracted of products", value=last_extraction_all['products'].sum())
m2.metric(label="Number of categories", value=len(green_db.get_category_summary().groupby('category')))
m3.metric(label="Number of merchants", value=len(green_db.get_category_summary().groupby('merchant')))

st.write("Latest job summary by merchant")
summary_ext, summary_scr = st.tabs(["📀Extraction", " 🤖Scraping"])
summary_ext.dataframe(last_extraction_all)
summary_scr.dataframe(last_scraping_all)

st.write("Categories by merchant")
st.caption("From latest products extraction")
cat_chart, cat_df = st.tabs(["📊Chart", "📓Data"])
cat_chart.plotly_chart(category_stack_bars(green_db.get_category_summary()), use_container_width=True)
cat_df.dataframe(green_db.get_category_summary().pivot_table(values='products', index=['category'], columns='merchant', fill_value=0))

st.write("Scraping and Extraction all timestamps")
alltimes_chart, alltimes_df = st.tabs(["📊Chart", "📓Data"])
alltimes_chart.plotly_chart(timeline(), use_container_width=True)
alltimes_df.dataframe(all_summ)
st.write("Scraping and Extraction all timestamps by merchant")
st.dataframe(all_pivot)

#Bar chart with cummulatives, one bar scraped and one extracted
st.write("Attribute overview")
#·procust with null attributes vs total number of products

st.subheader("Sustainability labels overview")
sus1, sus2, sus3 = st.columns(3)
sus1.write("Sustainability label's last update:")
sus2.write(green_db.last_update_sustainability_labels()[0].date())
sus3.metric(label="Labels in use", value=len(freq))
st.write("Products by sustainability labels")
st.dataframe(freq.sort_values(by='products', ascending=False))



