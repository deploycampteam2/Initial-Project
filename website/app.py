import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="ExploreIndonesia - Tourism Recommendations",
    page_icon="🏝️",
    layout="wide"
)

# Title
st.title("🏝️ ExploreIndonesia - Discover Amazing Destinations")
st.markdown("**Temukan destinasi wisata terbaik di Indonesia dengan rekomendasi yang dipersonalisasi**")
st.markdown("---")

# Sidebar
st.sidebar.header("🎯 Filter Wisata")
st.sidebar.markdown("### 📍 Pilih Preferensi Anda")

# Filter options
region_filter = st.sidebar.selectbox(
    "Pilih Wilayah:",
    ["Semua Wilayah", "Jawa", "Sumatera", "Kalimantan", "Sulawesi", "Papua", "Bali & Nusa Tenggara", "Maluku"]
)

category_filter = st.sidebar.multiselect(
    "Kategori Wisata:",
    ["Pantai", "Gunung", "Budaya", "Kuliner", "Sejarah", "Alam", "Adventure"],
    default=["Pantai", "Budaya", "Alam"]
)

budget_range = st.sidebar.slider(
    "Budget per Hari (Rp):",
    min_value=100000,
    max_value=2000000,
    value=(300000, 1000000),
    step=100000,
    format="Rp %d"
)

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🏖️ Total Destinasi", 
        value="1,247", 
        delta="89 baru"
    )

with col2:
    st.metric(
        label="⭐ Rating Rata-rata", 
        value="4.6/5", 
        delta="0.2"
    )

with col3:
    st.metric(
        label="👥 Traveler Aktif", 
        value="25,678", 
        delta="3,456"
    )

with col4:
    st.metric(
        label="📝 Review Bulan Ini", 
        value="4,892", 
        delta="892"
    )

st.markdown("---")

# Sample tourism data
@st.cache_data
def load_tourism_data():
    destinations = [
        "Raja Ampat", "Borobudur", "Komodo Island", "Lake Toba", "Bromo Tengger", 
        "Bali Beaches", "Yogyakarta", "Tanjung Lesung", "Bunaken", "Lombok"
    ]
    
    regions = [
        "Papua", "Jawa", "Nusa Tenggara", "Sumatera", "Jawa", 
        "Bali & Nusa Tenggara", "Jawa", "Banten", "Sulawesi", "Nusa Tenggara"
    ]
    
    categories = [
        "Alam", "Budaya", "Alam", "Alam", "Gunung",
        "Pantai", "Budaya", "Pantai", "Alam", "Pantai"
    ]
    
    # Generate data for the last 30 days
    dates = pd.date_range('2024-11-01', periods=30)
    
    data = []
    for date in dates:
        for i, dest in enumerate(destinations):
            data.append({
                'Date': date,
                'Destination': dest,
                'Region': regions[i],
                'Category': categories[i],
                'Visitors': np.random.randint(50, 500),
                'Rating': round(np.random.uniform(4.0, 5.0), 1),
                'Reviews': np.random.randint(5, 50),
                'Budget_Min': np.random.randint(200, 500) * 1000,
                'Budget_Max': np.random.randint(800, 1500) * 1000
            })
    
    return pd.DataFrame(data)

# Load data
df = load_tourism_data()

# Filter data based on sidebar selections
filtered_df = df.copy()

if region_filter != "Semua Wilayah":
    filtered_df = filtered_df[filtered_df['Region'] == region_filter]

if category_filter:
    filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Popularitas Destinasi (30 Hari Terakhir)")
    popularity_data = filtered_df.groupby('Destination')['Visitors'].sum().sort_values(ascending=False).head(10)
    fig_popularity = px.bar(
        x=popularity_data.values, 
        y=popularity_data.index,
        orientation='h',
        title="Destinasi Paling Populer",
        labels={'x': 'Total Pengunjung', 'y': 'Destinasi'}
    )
    fig_popularity.update_layout(height=400)
    st.plotly_chart(fig_popularity, use_container_width=True)

with col2:
    st.subheader("⭐ Rating vs Jumlah Review")
    rating_data = filtered_df.groupby('Destination').agg({
        'Rating': 'mean',
        'Reviews': 'sum',
        'Category': 'first'
    }).reset_index()
    
    fig_rating = px.scatter(
        rating_data, 
        x='Reviews', 
        y='Rating',
        size='Reviews',
        color='Category',
        hover_name='Destination',
        title="Korelasi Rating dan Jumlah Review"
    )
    fig_rating.update_layout(height=400)
    st.plotly_chart(fig_rating, use_container_width=True)

# Regional distribution
st.subheader("🗺️ Distribusi Destinasi per Wilayah")
region_data = filtered_df.groupby('Region').agg({
    'Visitors': 'sum',
    'Rating': 'mean'
}).reset_index()

fig_region = px.pie(
    region_data, 
    values='Visitors', 
    names='Region',
    title="Distribusi Pengunjung per Wilayah"
)
st.plotly_chart(fig_region, use_container_width=True)

# Top recommendations
st.subheader("🎯 Rekomendasi Destinasi Untuk Anda")

# Simple recommendation based on filters
top_destinations = filtered_df.groupby('Destination').agg({
    'Rating': 'mean',
    'Visitors': 'sum',
    'Reviews': 'sum',
    'Region': 'first',
    'Category': 'first',
    'Budget_Min': 'mean',
    'Budget_Max': 'mean'
}).reset_index()

# Score calculation (simple weighted scoring)
top_destinations['Score'] = (
    top_destinations['Rating'] * 0.4 + 
    (top_destinations['Visitors'] / top_destinations['Visitors'].max()) * 5 * 0.3 +
    (top_destinations['Reviews'] / top_destinations['Reviews'].max()) * 5 * 0.3
)

top_destinations = top_destinations.sort_values('Score', ascending=False).head(5)

# Display recommendations
for idx, row in top_destinations.iterrows():
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**🏆 {row['Destination']}**")
            st.write(f"📍 {row['Region']} • 🏷️ {row['Category']}")
            st.write(f"⭐ {row['Rating']:.1f}/5 ({int(row['Reviews'])} reviews)")
        
        with col2:
            st.write("💰 **Budget Range**")
            st.write(f"Rp {int(row['Budget_Min']):,} - {int(row['Budget_Max']):,}")
        
        with col3:
            st.write("📈 **Popularity**")
            st.write(f"{int(row['Visitors'])} pengunjung")
            
        st.markdown("---")

# Recent activity table
st.subheader("📋 Aktivitas Terkini")
recent_data = filtered_df.tail(10)[['Date', 'Destination', 'Region', 'Category', 'Visitors', 'Rating']]
recent_data['Date'] = recent_data['Date'].dt.strftime('%d %b %Y')
st.dataframe(recent_data, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🌍 ExploreIndonesia • 🎯 Powered by AI Recommendations • 📱 Coming Soon: Mobile App</p>
        <p>💡 Membantu Anda menemukan destinasi impian di Nusantara</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%d %B %Y, %H:%M WIB")),
    unsafe_allow_html=True
)