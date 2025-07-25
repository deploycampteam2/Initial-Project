import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Initial Project Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 Initial Project - Streamlit Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("Dashboard Controls")
st.sidebar.markdown("### 📊 Data Visualization")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🏆 Total Users", 
        value="1,234", 
        delta="123"
    )

with col2:
    st.metric(
        label="💰 Revenue", 
        value="$45,678", 
        delta="$5,678"
    )

with col3:
    st.metric(
        label="📈 Growth", 
        value="23.5%", 
        delta="2.1%"
    )

st.markdown("---")

# Sample data
@st.cache_data
def load_data():
    dates = pd.date_range('2024-01-01', periods=100)
    data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(100, 1000, 100),
        'Users': np.random.randint(50, 500, 100),
        'Revenue': np.random.randint(1000, 10000, 100)
    })
    return data

# Load data
df = load_data()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Over Time")
    fig_sales = px.line(df, x='Date', y='Sales', title="Daily Sales")
    st.plotly_chart(fig_sales, use_container_width=True)

with col2:
    st.subheader("👥 User Growth")
    fig_users = px.bar(df.tail(20), x='Date', y='Users', title="Recent User Activity")
    st.plotly_chart(fig_users, use_container_width=True)

# Data table
st.subheader("📋 Recent Data")
st.dataframe(df.tail(10), use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🎯 Deployed via GitHub Actions • 🐳 Powered by Docker • ⚡ Built with Streamlit & UV</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)