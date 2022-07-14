import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Env variables
os.environ["POSTGRES_SCRAPING_USER"] = "scraping"
os.environ["POSTGRES_SCRAPING_PASSWORD"] = "scraping1992"
os.environ["POSTGRES_SCRAPING_HOST"] = "127.0.0.1"
os.environ["POSTGRES_SCRAPING_PORT"] = "5432"
os.environ["POSTGRES_GREEN_DB_USER"] = "green-db"
os.environ["POSTGRES_GREEN_DB_PASSWORD"] = "green1992"
os.environ["POSTGRES_GREEN_DB_HOST"] = "127.0.0.1"
os.environ["POSTGRES_GREEN_DB_PORT"] = "5432"
os.environ["REDIS_PASSWORD"] = "redi1992"
from database.database.connection import GreenDB

green_db = GreenDB()
# scraping = Scraping()

all_extraction = pd.DataFrame(
    green_db.get_timestamps_by_merchant(), columns=["Merchant", "Timestamp", "Products Extracted"]
)
all_extraction["Timestamp"] = pd.to_datetime(all_extraction["Timestamp"]).dt.date
pivot = all_extraction.pivot_table("Products Extracted", ["Timestamp"], "Merchant", fill_value=0)


def category_mosaic_chart(df):
    cat_by_merchant = df.pivot_table('products', 'category', 'merchant', fill_value=0)

    cat_by_merchant_matrix = list(map(list, zip(*cat_by_merchant.to_numpy())))
    print(cat_by_merchant)
    data = dict(zip(cat_by_merchant.index, cat_by_merchant.to_numpy()))
    print(data)
    data_2 = dict(zip(cat_by_merchant.columns, cat_by_merchant_matrix))

    totals = df.groupby(by=['merchant']).sum()

    all_products = int(df['products'].sum())
    totals['percentage'] = [round((i/all_products * 100), 1) for i in (totals['products'])]
    widths = np.array(totals['percentage'])
    labels = cat_by_merchant.columns
    #return data

    for key in data:
        fig.add_trace(go.Bar(
            name=key,
            y=data[key],
            x=np.cumsum(widths) - widths,
            width=widths,
            offset=0,
            customdata=np.transpose([labels, widths * data[key]]),
            texttemplate="%{y}",
            textposition="inside",
            textangle=0,
            textfont_color="white",
            hovertemplate=""
        ))

    fig.update_xaxes(
        tickvals=np.cumsum(widths) - widths / 2,
        ticktext=["%s<br>%d" % (l, w) for l, w in zip(labels, widths)]
    )

    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(range=[0, totals['products'].min()])

    fig.update_layout(
        title_text="Categories per Merchant in GreenDB",
        barmode="stack",
        uniformtext=dict(mode="hide", minsize=10),
    )
    return fig

def timeline(df):
    df['timestamp'] = df['timestamp'].dt.date
    all_timestamps = df.groupby(by=['timestamp']).sum().sort_values(by='timestamp', ascending=False)
    fig = px.bar(all_timestamps, y='products_extracted', x=all_timestamps.index)
    return fig

timeline(green_db.get_timestamps_by_merchant())

def category_stack_bars(df):
    fig = px.bar(df, x="category", y='products', color ='merchant', text='products')
    return (fig)

