from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

from db import run_sql
import queries

load_dotenv()

st.set_page_config(page_title="Shopping Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Shopping Analytics Dashboard")
st.caption("Python + SQL (Postgres) + Streamlit — deployable from GitHub as a live site.")

def fetch_df(sql: str, params: dict | None = None):
    res = run_sql(sql, params or {})
    return pd.DataFrame(res.fetchall(), columns=res.keys())

# --- Get data coverage (min/max dates) from the DB ---
coverage = fetch_df(
    "SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM orders;",
    {}
)

if coverage.empty or pd.isna(coverage.loc[0, "min_date"]) or pd.isna(coverage.loc[0, "max_date"]):
    st.error("No data found in the database (orders table is empty). Load data first.")
    st.stop()

min_date = pd.to_datetime(coverage.loc[0, "min_date"]).date()
max_date = pd.to_datetime(coverage.loc[0, "max_date"]).date()

# --- Filters (defaults auto-fit to dataset) ---
colA, colB, colC = st.columns([2, 2, 1])
with colA:
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
with colB:
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
with colC:
    top_n = st.selectbox("Top N items", [5, 10, 15, 25], index=1)

# Ensure start <= end
if start_date > end_date:
    st.warning("Start date cannot be after end date. Please adjust your range.")
    st.stop()

# Data coverage line (D)
range_days = (max_date - min_date).days + 1
st.caption(f"Data coverage: {min_date} → {max_date} ({range_days} days)")

params = {"start_date": start_date, "end_date": end_date, "limit": int(top_n)}

totals = fetch_df(queries.TOTALS, params)
if totals.empty:
    st.warning("No data found for that date range.")
    st.stop()

t = totals.iloc[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", f"{int(t['total_orders'])}")
k2.metric("Revenue", f"${float(t['revenue'] or 0):,.2f}")
k3.metric("Avg Order Value", f"${float(t['avg_order_value'] or 0):,.2f}")
k4.metric("Avg Discount", f"{float(t['avg_discount'] or 0):.1f}%")

st.divider()

left, right = st.columns(2)

rev_cat = fetch_df(queries.REVENUE_BY_CATEGORY, params)
left.plotly_chart(px.bar(rev_cat, x="category", y="revenue", title="Revenue by Category"), use_container_width=True)

rev_gender = fetch_df(queries.REVENUE_BY_GENDER, params)
right.plotly_chart(px.bar(rev_gender, x="gender", y="revenue", title="Revenue by Gender"), use_container_width=True)

st.divider()

bottom_left, bottom_right = st.columns(2)

top_items = fetch_df(queries.TOP_ITEMS, params)
bottom_left.plotly_chart(
    px.bar(top_items, x="item", y="revenue", title=f"Top {top_n} Items by Revenue"),
    use_container_width=True
)

subs = fetch_df(queries.SUBSCRIPTION_SPLIT, params)
bottom_right.plotly_chart(
    px.pie(subs, names="subscription", values="revenue", title="Revenue Split: Subscription"),
    use_container_width=True
)

st.divider()
st.subheader("Raw Rows (preview)")

preview_mode = st.radio(
    "Preview order",
    ["Earliest in range", "Latest in range"],
    horizontal=True
)

order_dir = "ASC" if preview_mode == "Earliest in range" else "DESC"

preview_sql = f"""
SELECT *
FROM orders
WHERE order_date BETWEEN :start_date AND :end_date
ORDER BY order_date {order_dir}, order_id {order_dir}
LIMIT 50;
"""

st.dataframe(
    fetch_df(preview_sql, {
        "start_date": start_date,
        "end_date": end_date
    })
)
