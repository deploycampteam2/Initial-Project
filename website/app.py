import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json
import os
from typing import List, Dict, Optional
import time
from streamlit_option_menu import option_menu

# Page config
st.set_page_config(
    page_title="ExploreIndonesia - AI Tourism Recommendations",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .recommendation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #FF6B35;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: white;
    }
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_api_data(endpoint: str, params: dict = None) -> dict:
    """Get data from API with error handling"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("❌ Tidak dapat terhubung ke API. Pastikan server API berjalan di http://localhost:8000")
        return {}
    except requests.exceptions.Timeout:
        st.error("⏰ Timeout connecting to API")
        return {}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}

def post_api_data(endpoint: str, data: dict) -> dict:
    """Post data to API with error handling"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/{endpoint}", 
            json=data, 
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("❌ Tidak dapat terhubung ke API. Pastikan server API berjalan.")
        return {}
    except requests.exceptions.Timeout:
        st.error("⏰ Timeout connecting to API")
        return {}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_cities() -> List[str]:
    """Get available cities from API"""
    cities = get_api_data("cities")
    return cities if isinstance(cities, list) else ["Jakarta", "Yogyakarta", "Bandung", "Semarang", "Surabaya"]

@st.cache_data(ttl=600)
def get_categories() -> List[str]:
    """Get available categories from API"""
    categories = get_api_data("categories")
    return categories if isinstance(categories, list) else ["Budaya", "Taman Hiburan", "Cagar Alam", "Bahari"]

@st.cache_data(ttl=600)
def get_stats() -> dict:
    """Get statistics from API"""
    return get_api_data("stats")

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🏝️ ExploreIndonesia</h1>
    <h3>Discover Amazing Destinations with AI-Powered Recommendations</h3>
    <p>Temukan destinasi wisata terbaik di Indonesia dengan teknologi Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# Navigation Menu
selected = option_menu(
    menu_title=None,
    options=["🏠 Beranda", "🔍 Cari Wisata", "📊 Statistik", "ℹ️ Tentang"],
    icons=["house", "search", "graph-up", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected == "🏠 Beranda":
    # Load stats data
    stats = get_stats()
    
    # Main metrics
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🏖️ Total Destinasi</h3>
                <h2>{}</h2>
                <p>Destinasi tersedia</p>
            </div>
            """.format(stats.get('total_destinations', 'N/A')), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>⭐ Rating Rata-rata</h3>
                <h2>{}/5</h2>
                <p>Kualitas destinasi</p>
            </div>
            """.format(stats.get('avg_rating', 'N/A')), unsafe_allow_html=True)
        
        with col3:
            cities = stats.get('cities', [])
            st.markdown("""
            <div class="metric-card">
                <h3>🏙️ Kota Tersedia</h3>
                <h2>{}</h2>
                <p>Kota di Indonesia</p>
            </div>
            """.format(len(cities) if cities else 'N/A'), unsafe_allow_html=True)
        
        with col4:
            categories = stats.get('categories', [])
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Kategori Wisata</h3>
                <h2>{}</h2>
                <p>Jenis destinasi</p>
            </div>
            """.format(len(categories) if categories else 'N/A'), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick recommendations
    st.subheader("🎯 Rekomendasi Populer")
    
    with st.spinner("Mengambil rekomendasi..."):
        recommendations = get_api_data("recommendations", {"top_n": 6})
    
    if recommendations:
        cols = st.columns(2)
        for idx, rec in enumerate(recommendations[:6]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4>🏛️ {rec.get('Place_Name', 'Unknown')}</h4>
                    <p><strong>📍 Lokasi:</strong> {rec.get('City', 'Unknown')}</p>
                    <p><strong>🏷️ Kategori:</strong> {rec.get('Category', 'Unknown')}</p>
                    <p><strong>⭐ Rating:</strong> {rec.get('Rating', 'N/A')}/5</p>
                    <p><strong>💰 Harga:</strong> Rp {rec.get('Price', 0):,}</p>
                    <p><strong>🔢 Score:</strong> {rec.get('score', 0):.2f}</p>
                    <p><small>{rec.get('Description', 'Tidak ada deskripsi')[:100]}...</small></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Tidak dapat mengambil rekomendasi. Pastikan API berjalan.")

elif selected == "🔍 Cari Wisata":
    st.header("🔍 Cari Destinasi Wisata")
    
    # Get available options
    cities = get_cities()
    categories = get_categories()
    
    # Sidebar filters
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>🎯 Filter Pencarian</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options
    location = st.sidebar.selectbox(
        "📍 Pilih Kota:",
        ["Semua Kota"] + cities,
        index=0
    )
    
    category = st.sidebar.selectbox(
        "🏷️ Kategori Wisata:",
        ["Semua Kategori"] + categories,
        index=0
    )
    
    price_category = st.sidebar.selectbox(
        "💰 Kategori Harga:",
        ["Semua Harga", "murah", "menengah", "mahal"],
        index=0
    )
    
    min_rating = st.sidebar.slider(
        "⭐ Rating Minimal:",
        min_value=3.0,
        max_value=5.0,
        value=4.0,
        step=0.1,
        format="%.1f"
    )
    
    interests = st.sidebar.text_area(
        "🎯 Minat/Kata Kunci:",
        placeholder="Contoh: museum, sejarah, budaya (pisahkan dengan koma)",
        help="Masukkan kata kunci yang menggambarkan minat Anda"
    )
    
    top_n = st.sidebar.slider(
        "📊 Jumlah Rekomendasi:",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )
    
    # Search button
    search_button = st.sidebar.button("🔍 Cari Destinasi", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if search_button or 'search_results' not in st.session_state:
            # Prepare search parameters
            params = {
                "top_n": top_n,
                "min_rating": min_rating
            }
            
            if location != "Semua Kota":
                params["location"] = location
            if category != "Semua Kategori":
                params["category"] = category
            if price_category != "Semua Harga":
                params["price_category"] = price_category
            if interests.strip():
                params["interests"] = interests.strip()
            
            # Search recommendations
            with st.spinner("Mencari rekomendasi terbaik untuk Anda..."):
                search_results = get_api_data("recommendations", params)
                st.session_state['search_results'] = search_results
        
        # Display results
        if 'search_results' in st.session_state and st.session_state['search_results']:
            st.subheader(f"📋 Hasil Pencarian ({len(st.session_state['search_results'])} destinasi)")
            
            for idx, rec in enumerate(st.session_state['search_results'], 1):
                with st.expander(f"{idx}. {rec.get('Place_Name', 'Unknown')}", expanded=idx<=3):
                    col_info, col_details = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        **📍 Lokasi:** {rec.get('City', 'Unknown')}  
                        **🏷️ Kategori:** {rec.get('Category', 'Unknown')}  
                        **⭐ Rating:** {rec.get('Rating', 'N/A')}/5  
                        **💰 Harga:** Rp {rec.get('Price', 0):,}  
                        **🏷️ Kategori Harga:** {rec.get('price_category', 'Unknown')}  
                        **🔢 AI Score:** {rec.get('score', 0):.3f}  
                        
                        **📝 Deskripsi:**  
                        {rec.get('Description', 'Tidak ada deskripsi tersedia')}
                        """)
                    
                    with col_details:
                        # Create a simple rating visualization
                        rating = rec.get('Rating', 0)
                        stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
                        
                        st.markdown(f"""
                        **Rating Visual:**  
                        {stars}  
                        
                        **Rekomendasi Level:**  
                        {"🔥 Sangat Direkomendasikan" if rec.get('score', 0) > 0.8 
                         else "👍 Direkomendasikan" if rec.get('score', 0) > 0.6 
                         else "👌 Cukup Bagus"}
                        """)
        
        elif 'search_results' in st.session_state:
            st.warning("🤷‍♂️ Tidak ada destinasi yang cocok dengan kriteria pencarian Anda. Coba ubah filter pencarian.")
    
    with col2:
        st.subheader("💡 Tips Pencarian")
        st.info("""
        **🎯 Untuk hasil optimal:**
        - Gunakan kata kunci spesifik di bagian "Minat"
        - Coba kombinasi filter yang berbeda
        - Turunkan rating minimal jika hasil sedikit
        
        **🔍 Contoh kata kunci:**
        - museum, sejarah → untuk wisata budaya
        - pantai, laut → untuk wisata bahari
        - gunung, alam → untuk wisata alam
        """)
        
        if 'search_results' in st.session_state and st.session_state['search_results']:
            st.subheader("📊 Statistik Hasil")
            results = st.session_state['search_results']
            
            # Rating distribution
            ratings = [r.get('Rating', 0) for r in results]
            if ratings:
                fig_rating = px.histogram(
                    x=ratings, 
                    nbins=10,
                    title="Distribusi Rating",
                    labels={'x': 'Rating', 'y': 'Jumlah'}
                )
                st.plotly_chart(fig_rating, use_container_width=True)
            
            # Price category distribution
            price_cats = [r.get('price_category', 'Unknown') for r in results]
            price_dist = pd.Series(price_cats).value_counts()
            
            if len(price_dist) > 0:
                fig_price = px.pie(
                    values=price_dist.values,
                    names=price_dist.index,
                    title="Sebaran Kategori Harga"
                )
                st.plotly_chart(fig_price, use_container_width=True)

elif selected == "📊 Statistik":
    st.header("📊 Statistik Platform")
    
    # Get comprehensive stats
    stats = get_stats()
    
    if stats:
        st.subheader("📈 Overview Platform")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="🏛️ Total Destinasi",
                value=stats.get('total_destinations', 'N/A')
            )
            st.metric(
                label="⭐ Rating Rata-rata",
                value=f"{stats.get('avg_rating', 'N/A')}/5"
            )
        
        with col2:
            cities = stats.get('cities', [])
            categories = stats.get('categories', [])
            st.metric(
                label="🏙️ Jumlah Kota",
                value=len(cities) if cities else 'N/A'
            )
            st.metric(
                label="🎯 Jumlah Kategori",
                value=len(categories) if categories else 'N/A'
            )
        
        # Price category distribution
        if 'price_categories' in stats:
            st.subheader("💰 Distribusi Kategori Harga")
            price_data = stats['price_categories']
            
            fig_price = px.bar(
                x=list(price_data.keys()),
                y=list(price_data.values()),
                title="Jumlah Destinasi per Kategori Harga",
                labels={'x': 'Kategori Harga', 'y': 'Jumlah Destinasi'}
            )
            st.plotly_chart(fig_price, use_container_width=True)
        
        # Rating distribution
        if 'rating_distribution' in stats:
            st.subheader("⭐ Distribusi Rating")
            rating_stats = stats['rating_distribution']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Statistik Rating:**")
                for key, value in rating_stats.items():
                    if key in ['mean', 'min', 'max', 'std']:
                        st.write(f"- {key.title()}: {value:.2f}")
            
            with col2:
                # Simple rating breakdown visualization
                st.write("**Insight:**")
                avg_rating = rating_stats.get('mean', 0)
                if avg_rating >= 4.5:
                    st.success("🎉 Platform memiliki kualitas destinasi yang sangat baik!")
                elif avg_rating >= 4.0:
                    st.info("👍 Kualitas destinasi di atas rata-rata")
                else:
                    st.warning("⚠️ Ada ruang untuk peningkatan kualitas")
    else:
        st.error("Tidak dapat mengambil data statistik. Pastikan API berjalan.")

elif selected == "ℹ️ Tentang":
    st.header("ℹ️ Tentang ExploreIndonesia")
    
    st.markdown("""
    ## 🏝️ ExploreIndonesia
    
    **ExploreIndonesia** adalah platform rekomendasi destinasi wisata Indonesia yang menggunakan teknologi 
    Machine Learning untuk memberikan rekomendasi yang personal dan akurat.
    
    ### 🚀 Teknologi Yang Digunakan
    
    - **Backend API:** FastAPI dengan Python
    - **Machine Learning:** LightGBM Learning-to-Rank Model
    - **Frontend:** Streamlit
    - **Data Processing:** Pandas, NumPy, Scikit-learn
    - **Visualization:** Plotly
    
    ### 🎯 Fitur Utama
    
    1. **🔍 Pencarian Cerdas:** Cari destinasi berdasarkan preferensi dan minat
    2. **🤖 Rekomendasi AI:** Sistem rekomendasi berbasis Machine Learning
    3. **📊 Filter Lengkap:** Filter berdasarkan lokasi, kategori, harga, dan rating
    4. **📈 Statistik Real-time:** Data dan insights tentang destinasi wisata
    
    ### 🏛️ Data Destinasi
    
    Platform ini menyediakan informasi tentang **437+ destinasi wisata** di **5 kota besar** Indonesia:
    - Jakarta
    - Yogyakarta  
    - Bandung
    - Semarang
    - Surabaya
    
    ### 📱 Status API
    """)
    
    # API Status Check
    with st.spinner("Mengecek status API..."):
        api_status = get_api_data("")
    
    if api_status:
        st.success("✅ API Status: Online")
        st.json({
            "Message": api_status.get("message", "N/A"),
            "Version": api_status.get("version", "N/A"),
            "ML Model Loaded": api_status.get("ml_model_loaded", "N/A")
        })
    else:
        st.error("❌ API Status: Offline")
        st.warning("⚠️ Pastikan server API berjalan di http://localhost:8000")
    
    st.markdown("""
    ### 👨‍💻 Pengembang
    
    Dikembangkan menggunakan teknologi modern untuk memberikan pengalaman terbaik dalam 
    menemukan destinasi wisata Indonesia.
    
    ### 📞 Dukungan
    
    Jika Anda mengalami masalah atau memiliki saran, silakan hubungi tim pengembang.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
            <p>🌍 ExploreIndonesia • 🤖 Powered by AI • 📱 Built with Streamlit</p>
            <p>💡 Helping you discover Indonesia's hidden gems</p>
            <p>Last updated: {datetime.now().strftime("%d %B %Y, %H:%M WIB")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


