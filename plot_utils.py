import plotly.express as px

def revenue_trend(df):
    df_grouped = df.groupby("date")["revenue"].sum().reset_index()
    fig = px.line(df_grouped, x="date", y="revenue", title="Revenue Over Time")
    return fig

def revenue_by_store(df):
    fig = px.bar(df.groupby("store_id")["revenue"].sum().reset_index(),
                 x="store_id", y="revenue", title="Revenue by Store")
    return fig

def product_pie_chart(df):
    fig = px.pie(df.groupby("product_id")["revenue"].sum().reset_index(),
                 values="revenue", names="product_id", title="Revenue Share by Product")
    return fig
