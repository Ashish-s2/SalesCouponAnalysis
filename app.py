import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import calendar
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- Streamlit Config ---
st.set_page_config(
    page_title="Coupon Intelligence Dashboard",
    layout="wide",
    page_icon="🎟️"
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("online_coupon_analysis_dataset.csv")
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

# --- App Title ---
st.markdown("""
    <style>
    .main {background-color: #f5f7fb;}
    h1 {text-align: center; color: #2e3b4e;}
    h3 {color: #4e4376;}
    </style>
""", unsafe_allow_html=True)

st.title(" Coupon Intelligence Dashboard - Ultra Edition")
st.markdown("""
Built to extract smart insights from online coupon sales data.
Designed for analysts, strategists, and brands that want to win smarter.
""")

# --- Load Dataset ---
df = load_data()
st.sidebar.title("⚙️ Filters")

# --- Sidebar Filters ---
st.sidebar.markdown("##  Refine Data View")
regions = st.sidebar.multiselect(" Select Region(s)", df['region'].unique(), default=df['region'].unique())
categories = st.sidebar.multiselect(" Select Product Category", df['product_category'].unique(), default=df['product_category'].unique())
coupons = st.sidebar.multiselect(" Select Coupon Type", df['coupon_type'].unique(), default=df['coupon_type'].unique())
date_range = st.sidebar.date_input(" Select Date Range", [df['order_date'].min(), df['order_date'].max()])
min_discount = st.sidebar.slider(" Minimum Discount %", 0, 100, 0)

# --- Apply Filters ---
df_filtered = df[
    (df['region'].isin(regions)) &
    (df['product_category'].isin(categories)) &
    (df['coupon_type'].isin(coupons)) &
    (df['order_date'] >= pd.to_datetime(date_range[0])) &
    (df['order_date'] <= pd.to_datetime(date_range[1])) &
    (df['discount_percentage'] >= min_discount)
]

# --- KPI Section ---
st.markdown("---")
st.subheader(" Performance KPIs")
total_orders = len(df_filtered)
total_revenue = df_filtered['final_amount'].sum()
avg_discount = df_filtered['discount_percentage'].mean()
coupon_usage_rate = df_filtered['coupon_used'].mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric(" Orders", f"{total_orders:,}")
col2.metric(" Revenue", f"₹{total_revenue:,.0f}")
col3.metric(" Avg Discount %", f"{avg_discount:.2f}%")
col4.metric(" Coupon Usage Rate", f"{coupon_usage_rate:.1f}%")

# --- Monthly Sales Trend ---
st.markdown("---")
st.subheader(" Monthly Revenue Trend")
monthly = df_filtered.groupby(['year', 'month_name'])['final_amount'].sum().reset_index()
monthly['month_num'] = monthly['month_name'].apply(lambda x: list(calendar.month_name).index(x))
monthly = monthly.sort_values(['year', 'month_num'])
fig1 = px.line(monthly, x='month_name', y='final_amount', color='year', markers=True, title="Revenue per Month")
st.plotly_chart(fig1, use_container_width=True)

# --- ROI Bubble ---
st.subheader(" ROI by Coupon Type")
roi_df = df_filtered.groupby('coupon_type')[['final_amount', 'discount_amount']].sum().reset_index()
roi_df['ROI'] = roi_df['final_amount'] / roi_df['discount_amount']
fig2 = px.scatter(roi_df, x='discount_amount', y='final_amount', color='coupon_type', size='ROI', hover_name='coupon_type', title="ROI Effectiveness Bubble Chart")
st.plotly_chart(fig2, use_container_width=True)

# --- Region Heatmap ---
st.subheader(" Region vs Coupon Type Heatmap")
region_coupon = df_filtered.groupby(['region', 'coupon_type']).size().unstack().fillna(0)
fig3 = px.imshow(region_coupon, text_auto=True, color_continuous_scale='blues')
st.plotly_chart(fig3, use_container_width=True)

# --- Income vs Spend ---
st.subheader(" Income vs Spend Relationship")
fig4 = px.scatter(df_filtered, x='customer_income', y='final_amount', color='sales_category', size='units_sold', hover_data=['product_category'])
st.plotly_chart(fig4, use_container_width=True)

# --- Donut: Category Share ---
st.subheader(" Product Category Share")
category_dist = df_filtered['product_category'].value_counts().reset_index()
category_dist.columns = ['product_category', 'count']
fig5 = px.pie(category_dist, names='product_category', values='count', hole=0.5, title="Distribution of Product Categories")
st.plotly_chart(fig5, use_container_width=True)

# --- Top Coupon Per Product ---
st.subheader(" Best Coupon Type per Product")
best_coupon = df_filtered.groupby(['product_category', 'coupon_type'])['final_amount'].mean().reset_index()
best_coupon = best_coupon.sort_values(['product_category', 'final_amount'], ascending=[True, False])
best_per_cat = best_coupon.drop_duplicates('product_category')
st.dataframe(best_per_cat.reset_index(drop=True), use_container_width=True)

# --- Download Button ---
st.markdown("---")
st.download_button(" Download Filtered Dataset as CSV", data=df_filtered.to_csv(index=False), file_name="filtered_coupon_data.csv")

# --- Footer ---
st.markdown("""
---
<center>
<h5>Built with ❤️ by Ashish Sahu</h5>
<p style='font-size: 0.8rem;'>Streamlit Ultra Edition | Advanced Visuals + Dynamic Filters + ROI Engine</p>
</center>
""", unsafe_allow_html=True)
