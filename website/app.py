import streamlit as st
import pandas as pd
import requests
import json
import os
from PIL import Image
import random
from typing import List, Dict, Optional

# Page config
st.set_page_config(
    page_title="ExploreIndonesia - Rekomendasi Wisata Indonesia",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .destination-card {
        background: white;
        border-radius: 15px;
        padding: 0;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        overflow: hidden;
        border: 1px solid #f0f0f0;
    }
    
    .destination-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .card-content {
        padding: 1.5rem;
    }
    
    .city-badge {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .rating-badge {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .price-badge {
        background: #17a2b8;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
    }
    
    .category-tag {
        background: #6f42c1;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        display: inline-block;
        margin-right: 0.3rem;
    }
    
    .search-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    
    .destination-image {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-radius: 15px 15px 0 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.7rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .stat-item {
        text-align: center;
        color: white;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        display: block;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def format_price(price):
    """Format price to Indonesian Rupiah"""
    if price == 0:
        return "Gratis"
    return f"Rp {price:,.0f}".replace(",", ".")

def get_image_path(place_name, place_id=None):
    """Get image path for a destination"""
    # Try to find matching image folder
    image_base = "/app/image"  # Path in Docker container
    
    # If we have place_id, try to match with folder pattern
    if place_id:
        folder_pattern = f"{place_id:03d}_"
        for folder in os.listdir(image_base) if os.path.exists(image_base) else []:
            if folder.startswith(folder_pattern):
                images = [f for f in os.listdir(os.path.join(image_base, folder)) if f.endswith('.jpg')]
                if images:
                    return os.path.join(image_base, folder, images[0])
    
    # Fallback: try to match by name
    place_normalized = place_name.replace(" ", "_").replace("(", "").replace(")", "")
    if os.path.exists(image_base):
        for folder in os.listdir(image_base):
            if place_normalized.lower() in folder.lower():
                images = [f for f in os.listdir(os.path.join(image_base, folder)) if f.endswith('.jpg')]
                if images:
                    return os.path.join(image_base, folder, images[0])
    
    return None

def get_recommendations_from_api(location=None, min_rating=None, price_category=None, category=None, top_n=10):
    """Fetch recommendations from API"""
    try:
        params = {"top_n": top_n}
        if location:
            params["location"] = location
        if min_rating:
            params["min_rating"] = min_rating
        if price_category:
            params["price_category"] = price_category
        if category:
            params["category"] = category
            
        response = requests.get(f"{API_BASE_URL}/recommendations", params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Tidak dapat terhubung ke API: {str(e)}")
        return []

def display_destination_card(destination, col):
    """Display a destination card"""
    with col:
        with st.container():
            # Try to load and display image
            image_path = get_image_path(destination.get("Place_Name", ""), destination.get("Place_Id"))
            
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    st.image(image, use_column_width=True, caption="")
                except Exception:
                    st.image("https://via.placeholder.com/400x250/667eea/white?text=No+Image", use_column_width=True)
            else:
                st.image("https://via.placeholder.com/400x250/667eea/white?text=No+Image", use_column_width=True)
            
            # Card content
            st.markdown(f"""
            <div class="card-content">
                <div class="city-badge">{destination.get('City', 'Unknown')}</div>
                <h3 style="margin: 0.5rem 0; color: #2c3e50; font-size: 1.3rem;">{destination.get('Place_Name', 'Unknown')}</h3>
                <p style="color: #7f8c8d; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.4;">
                    {destination.get('Description', 'No description available')[:100]}...
                </p>
                <div style="margin: 1rem 0;">
                    <span class="category-tag">{destination.get('Category', 'General')}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <div>
                        <span class="rating-badge">⭐ {destination.get('Rating', 0)}</span>
                        <span class="price-badge">{format_price(destination.get('Price', 0))}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def main():
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 3rem; margin-bottom: 1rem; color: #2c3e50;">🏝️ ExploreIndonesia</h1>
        <p style="font-size: 1.2rem; color: #7f8c8d; max-width: 600px; margin: 0 auto;">
            Temukan destinasi wisata terbaik di Indonesia dengan rekomendasi personal yang dipowered AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search filters
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        city_filter = st.selectbox(
            "🏙️ Pilih Kota",
            ["", "Jakarta", "Yogyakarta", "Bandung", "Semarang", "Surabaya"],
            help="Filter destinasi berdasarkan kota"
        )
    
    with col2:
        category_filter = st.selectbox(
            "🎯 Kategori Wisata", 
            ["", "Budaya", "Taman Hiburan", "Cagar Alam", "Bahari", "Pusat Perbelanjaan", "Tempat Ibadah"],
            help="Pilih jenis wisata yang diminati"
        )
    
    with col3:
        min_rating = st.slider(
            "⭐ Rating Minimal", 
            min_value=3.0, max_value=5.0, value=4.0, step=0.1,
            help="Filter berdasarkan rating minimal"
        )
    
    with col4:
        price_category = st.selectbox(
            "💰 Kategori Harga",
            ["", "murah", "menengah", "mahal"],
            help="Filter berdasarkan rentang harga"
        )
    
    # Search button
    col_center = st.columns([2, 1, 2])[1]
    with col_center:
        search_clicked = st.button("🔍 Cari Rekomendasi", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get recommendations
    if search_clicked or not any([city_filter, category_filter, price_category]):
        with st.spinner("🔄 Mencari rekomendasi terbaik untuk Anda..."):
            recommendations = get_recommendations_from_api(
                location=city_filter if city_filter else None,
                min_rating=min_rating,
                price_category=price_category if price_category else None,
                category=category_filter if category_filter else None,
                top_n=12
            )
        
        if recommendations:
            st.markdown(f"<h2 style='text-align: center; color: #2c3e50; margin: 2rem 0;'>✨ {len(recommendations)} Rekomendasi Terbaik Untuk Anda</h2>", unsafe_allow_html=True)
            
            # Display recommendations in grid
            cols_per_row = 3
            for i in range(0, len(recommendations), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, recommendation in enumerate(recommendations[i:i+cols_per_row]):
                    display_destination_card(recommendation, cols[j])
        
        else:
            st.warning("🔍 Tidak ada rekomendasi yang ditemukan dengan kriteria tersebut. Coba ubah filter pencarian Anda.")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; margin-top: 4rem; border-top: 1px solid #e9ecef; color: #6c757d;">
        <p>🏝️ <strong>ExploreIndonesia</strong> - Jelajahi keindahan Nusantara dengan AI</p>
        <p style="font-size: 0.9rem;">Dibuat dengan ❤️ untuk Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()