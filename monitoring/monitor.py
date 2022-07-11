import streamlit as st
import psycopg2
from spycopg2.extension import DATETIMEARRAY
import pandas as pd
from datetime import datetime

def init_connection(dbname):
    return psycopg2.connect(**st.secrets[dbname])

def _get_latest_timestamp(dbname):
    conn = init_connection(dbname)
    with conn.cursor() as cur:
        cur.execute(f'SELECT max(TIMESTAMP) from "{dbname}";')
        return DATETIMEARRAY(cur.fetchall())

def run_query(dbname, query):
    conn = init_connection(dbname)
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


# rows = run_query("SELECT * from green-db LIMIT 10;")
get_timestamps_by_merchant = run_query("green-db", f'SELECT merchant, CAST(timestamp AS date) AS date, count(*) from "green-db" GROUP BY merchant, date ORDER BY date DESC')



#Starts visualization
st.title("GreenDB")
st.header("A Product-by-Product Sustainability Database")
st.subheader("Green-DB Statistics")
st.write("Latest timestamp of data extraction:")
latest_timestamp = str(_get_latest_timestamp("green-db"))
st.write(latest_timestamp[0])

df = pd.DataFrame(get_timestamps_by_merchant, columns=['Merchant', 'Timestamp', 'Products Extracted'])
st.dataframe(df)


st.subheader("Scraping Statistics")