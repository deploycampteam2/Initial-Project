import streamlit as st
import pandas as pd
import requests
import json
import os
from PIL import Image
import random
from typing import List, Dict, Optional
from streamlit_option_menu import option_menu
from streamlit_carousel import carousel
import math

# Page config
st.set_page_config(
    page_title="ExploreIndonesia - Rekomendasi Wisata Indonesia",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Real Indonesian cities from data with coordinates and destination counts
INDONESIAN_CITIES = {
    "Jakarta": {"lat": -6.1753924, "lon": 106.8271528, "region": "DKI Jakarta", "destinations": 84},
    "Yogyakarta": {"lat": -7.8006715, "lon": 110.3676551, "region": "DI Yogyakarta", "destinations": 126},
    "Bandung": {"lat": -6.7596377, "lon": 107.6097807, "region": "Jawa Barat", "destinations": 124},
    "Surabaya": {"lat": -7.3086482, "lon": 112.8216622, "region": "Jawa Timur", "destinations": 46},
    "Semarang": {"lat": -7.2098867, "lon": 110.3421119, "region": "Jawa Tengah", "destinations": 57}
}

# Custom CSS with improved geolocation features
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
    
    .location-info {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        display: inline-block;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    .city-stats {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin-top: 0.5rem;
        font-size: 0.8rem;
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
</style>
""", unsafe_allow_html=True)


def format_price(price):
    """Format price to Indonesian Rupiah"""
    if price == 0:
        return "Gratis"
    return f"Rp {price:,.0f}".replace(",", ".")

def get_destination_images(place_name, place_id=None, max_images=5):
    """Get multiple image paths for a destination"""
    image_base = "/app/image"
    images = []
    
    if place_id:
        folder_pattern = f"{place_id:03d}_"
        for folder in os.listdir(image_base) if os.path.exists(image_base) else []:
            if folder.startswith(folder_pattern):
                folder_images = [f for f in os.listdir(os.path.join(image_base, folder)) if f.endswith('.jpg')]
                if folder_images:
                    # Sort to get consistent order
                    folder_images.sort()
                    for img in folder_images[:max_images]:
                        images.append(os.path.join(image_base, folder, img))
                    break
    
    if not images:
        place_normalized = place_name.replace(" ", "_").replace("(", "").replace(")", "")
        if os.path.exists(image_base):
            for folder in os.listdir(image_base):
                if place_normalized.lower() in folder.lower():
                    folder_images = [f for f in os.listdir(os.path.join(image_base, folder)) if f.endswith('.jpg')]
                    if folder_images:
                        folder_images.sort()
                        for img in folder_images[:max_images]:
                            images.append(os.path.join(image_base, folder, img))
                        break
    
    return images if images else []

def get_image_path(place_name, place_id=None):
    """Get single image path for a destination (backward compatibility)"""
    images = get_destination_images(place_name, place_id, 1)
    return images[0] if images else None

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

def display_image_carousel(images, destination_id):
    """Display image carousel for destination using streamlit-carousel"""
    if not images:
        st.image("https://via.placeholder.com/400x250/667eea/white?text=No+Image", use_container_width=True)
        return
    
    # Filter existing images and prepare for carousel
    carousel_items = []
    for img_path in images:
        if os.path.exists(img_path):
            try:
                # Convert to base64 for carousel
                with open(img_path, "rb") as img_file:
                    import base64
                    img_base64 = base64.b64encode(img_file.read()).decode()
                    carousel_items.append({
                        "title": f"Gambar {len(carousel_items) + 1}",
                        "text": "",
                        "img": f"data:image/jpeg;base64,{img_base64}"
                    })
            except Exception as e:
                continue
    
    if not carousel_items:
        st.image("https://via.placeholder.com/400x250/667eea/white?text=No+Image", use_container_width=True)
        return
    
    # If only one image, display it directly
    if len(carousel_items) == 1:
        st.image(carousel_items[0]["img"], use_container_width=True)
        return
    
    # Use streamlit-carousel
    carousel(
        items=carousel_items,
        width=1.0,
        height=250,
        key=f"carousel_{destination_id}_{random.randint(1000, 9999)}"
    )

def display_destination_card(destination, col):
    """Display a destination card with image carousel"""
    with col:
        with st.container():
            # Get multiple images for carousel
            images = get_destination_images(
                destination.get("Place_Name", ""), 
                destination.get("Place_Id"), 
                max_images=5
            )
            
            # Display carousel
            display_image_carousel(images, destination.get("Place_Id", 0))
            
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

def get_user_location():
    """Get user location using JavaScript geolocation API"""
    geolocation_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    // Send location to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {lat: lat, lon: lon, success: true}
                    }, '*');
                },
                function(error) {
                    console.log("Geolocation error: ", error);
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {success: false, error: error.message}
                    }, '*');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        } else {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: {success: false, error: 'Geolocation not supported'}
            }, '*');
        }
    }
    
    // Auto-call when component loads
    getLocation();
    </script>
    """
    return geolocation_js

def homepage():
    """Homepage with location-based recommendations"""
    # Initialize location in session state
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = "Jakarta"
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 3rem; margin-bottom: 1rem; color: #2c3e50;">🏝️ ExploreIndonesia</h1>
        <p style="font-size: 1.2rem; color: #7f8c8d; max-width: 600px; margin: 0 auto;">
            Temukan destinasi wisata terbaik di sekitar Anda
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Location selection section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📍 Pilih Wilayah Anda")
        
        # City selection with real data
        city_options = []
        for city, info in INDONESIAN_CITIES.items():
            city_options.append(f"{city} ({info['destinations']} destinasi)")
        
        selected_display = st.selectbox(
            "Atau pilih kota secara manual:",
            city_options,
            index=0 if st.session_state.selected_city == "Jakarta" else 
                  1 if st.session_state.selected_city == "Yogyakarta" else
                  2 if st.session_state.selected_city == "Bandung" else
                  3 if st.session_state.selected_city == "Surabaya" else
                  4 if st.session_state.selected_city == "Semarang" else 0
        )
        
        # Extract city name from display
        selected_city = selected_display.split(" (")[0]
        st.session_state.selected_city = selected_city
        
        # Display current location info with stats
        city_info = INDONESIAN_CITIES[selected_city]
        st.markdown(f"""
        <div class="location-info">
            📍 Lokasi Terpilih: {selected_city}, {city_info['region']}
            <div class="city-stats">
                🏛️ {city_info['destinations']} destinasi tersedia
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Get recommendations for selected city
    st.markdown("### ✨ Rekomendasi Wisata di Sekitar Anda")
    
    with st.spinner("🔄 Mencari tempat wisata terbaik..."):
        # Get top 5 highest rated destinations from selected city
        recommendations = get_recommendations_from_api(
            location=selected_city,
            min_rating=3.0,  # Lower threshold to get more results
            top_n=50  # Get more results to sort by rating
        )
        
        # Sort by rating and take top 5
        if recommendations:
            recommendations.sort(key=lambda x: x.get('Rating', 0), reverse=True)
            recommendations = recommendations[:5]
    
    if recommendations:
        # Display 5 top-rated destinations
        st.markdown(f"<h4 style='text-align: center; color: #2c3e50; margin: 1rem 0;'>🏆 Top {len(recommendations)} Rating Tertinggi di {selected_city}</h4>", unsafe_allow_html=True)
        
        # Special layout for 5 items: 2 on top, 3 on bottom
        if len(recommendations) >= 3:
            # First row - 2 cards
            cols = st.columns(2)
            for i in range(min(2, len(recommendations))):
                display_destination_card(recommendations[i], cols[i])
            
            # Second row - 3 cards (if we have more than 2)
            if len(recommendations) > 2:
                cols = st.columns(3)
                for i in range(2, min(5, len(recommendations))):
                    display_destination_card(recommendations[i], cols[i-2])
        else:
            # Fallback for less than 3 recommendations
            cols_per_row = 2
            for i in range(0, len(recommendations), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, rec in enumerate(recommendations[i:i+cols_per_row]):
                    if j < len(cols):
                        display_destination_card(rec, cols[j])
        
        # Show more button
        st.markdown("---")
        col_center = st.columns([2, 1, 2])[1]
        with col_center:
            if st.button("🖼️ Lihat Galeri Lengkap", use_container_width=True):
                st.session_state.current_page = "🖼️ Galeri"
                st.rerun()
    else:
        st.warning(f"Tidak ada rekomendasi ditemukan untuk wilayah {selected_city}.")
        
        # Show alternative cities
        st.markdown("### 🌟 Coba Pilih Kota Lain:")
        other_cities = [city for city in INDONESIAN_CITIES.keys() if city != selected_city]
        
        cols = st.columns(len(other_cities))
        for i, city in enumerate(other_cities):
            with cols[i]:
                city_info = INDONESIAN_CITIES[city]
                if st.button(f"{city}\n({city_info['destinations']} destinasi)", key=f"alt_city_{city}"):
                    st.session_state.selected_city = city
                    st.rerun()

def recommendations_page():
    """Advanced recommendations page with full search"""
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem; color: #2c3e50;">🔍 Cari Rekomendasi</h1>
        <p style="font-size: 1.1rem; color: #7f8c8d; max-width: 600px; margin: 0 auto;">
            Temukan destinasi wisata dengan filter pencarian yang detail
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search filters
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        city_options = [""] + [f"{city} ({info['destinations']})" for city, info in INDONESIAN_CITIES.items()]
        city_display = st.selectbox(
            "🏙️ Pilih Kota",
            city_options,
            help="Filter destinasi berdasarkan kota"
        )
        city_filter = city_display.split(" (")[0] if city_display else ""
    
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
    
    # Number of results
    col_center = st.columns([2, 1, 2])[1]
    with col_center:
        num_results = st.slider("📊 Jumlah Hasil", min_value=5, max_value=20, value=12)
    
    # Search button
    col_center = st.columns([2, 1, 2])[1]
    with col_center:
        search_clicked = st.button("🔍 Cari Rekomendasi", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get and display results
    if search_clicked or st.session_state.get('auto_search', True):
        with st.spinner("🔄 Mencari rekomendasi terbaik untuk Anda..."):
            recommendations = get_recommendations_from_api(
                location=city_filter if city_filter else None,
                min_rating=min_rating,
                price_category=price_category if price_category else None,
                category=category_filter if category_filter else None,
                top_n=num_results
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
            
            # Show city statistics
            st.markdown("### 📊 Statistik Dataset")
            cols = st.columns(len(INDONESIAN_CITIES))
            
            for i, (city, info) in enumerate(INDONESIAN_CITIES.items()):
                with cols[i]:
                    st.metric(
                        label=f"🏙️ {city}",
                        value=f"{info['destinations']} destinasi",
                        delta=info['region']
                    )
        
        # Turn off auto search after first load
        st.session_state.auto_search = False

def gallery_page():
    """Gallery page showing all destinations"""
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem; color: #2c3e50;">🖼️ Galeri Wisata Indonesia</h1>
        <p style="font-size: 1.1rem; color: #7f8c8d; max-width: 600px; margin: 0 auto;">
            Jelajahi semua destinasi wisata terbaik di Indonesia
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        city_options = ["Semua Kota"] + [f"{city} ({info['destinations']})" for city, info in INDONESIAN_CITIES.items()]
        city_display = st.selectbox(
            "🏙️ Filter Kota",
            city_options,
            help="Filter destinasi berdasarkan kota"
        )
        city_filter = city_display.split(" (")[0] if city_display != "Semua Kota" else ""
    
    with col2:
        category_filter = st.selectbox(
            "🎯 Filter Kategori", 
            ["Semua Kategori", "Budaya", "Taman Hiburan", "Cagar Alam", "Bahari", "Pusat Perbelanjaan", "Tempat Ibadah"],
            help="Pilih jenis wisata yang diminati"
        )
        if category_filter == "Semua Kategori":
            category_filter = ""
    
    with col3:
        min_rating = st.slider(
            "⭐ Rating Minimal", 
            min_value=3.0, max_value=5.0, value=3.0, step=0.1,
            help="Filter berdasarkan rating minimal"
        )
    
    # Sort options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox(
            "📊 Urutkan berdasarkan",
            ["Rating (Tertinggi)", "Rating (Terendah)", "Nama (A-Z)", "Nama (Z-A)", "Harga (Terendah)", "Harga (Tertinggi)"]
        )
    
    with col2:
        per_page = st.selectbox(
            "📄 Hasil per halaman",
            [12, 24, 48, 100],
            index=1
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get all destinations (API has max limit of 50)
    with st.spinner("🔄 Memuat galeri destinasi..."):
        # Get maximum available destinations from API
        all_destinations = get_recommendations_from_api(
            location=city_filter if city_filter else None,
            min_rating=min_rating,
            category=category_filter if category_filter else None,
            top_n=50  # API maximum limit
        )
    
    if all_destinations:
        # Sort results
        if sort_by == "Rating (Tertinggi)":
            all_destinations.sort(key=lambda x: x.get('Rating', 0), reverse=True)
        elif sort_by == "Rating (Terendah)":
            all_destinations.sort(key=lambda x: x.get('Rating', 0))
        elif sort_by == "Nama (A-Z)":
            all_destinations.sort(key=lambda x: x.get('Place_Name', ''))
        elif sort_by == "Nama (Z-A)":
            all_destinations.sort(key=lambda x: x.get('Place_Name', ''), reverse=True)
        elif sort_by == "Harga (Terendah)":
            all_destinations.sort(key=lambda x: x.get('Price', 0))
        elif sort_by == "Harga (Tertinggi)":
            all_destinations.sort(key=lambda x: x.get('Price', 0), reverse=True)
        
        # Pagination
        total_destinations = len(all_destinations)
        total_pages = (total_destinations + per_page - 1) // per_page
        
        if 'gallery_page_num' not in st.session_state:
            st.session_state.gallery_page_num = 1
        
        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Sebelumnya", disabled=st.session_state.gallery_page_num <= 1):
                st.session_state.gallery_page_num -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <strong>Halaman {st.session_state.gallery_page_num} dari {total_pages}</strong><br>
                <small>Menampilkan {total_destinations} destinasi</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("Selanjutnya ➡️", disabled=st.session_state.gallery_page_num >= total_pages):
                st.session_state.gallery_page_num += 1
                st.rerun()
        
        # Calculate slice for current page
        start_idx = (st.session_state.gallery_page_num - 1) * per_page
        end_idx = start_idx + per_page
        page_destinations = all_destinations[start_idx:end_idx]
        
        # Display destinations
        st.markdown(f"<h3 style='text-align: center; color: #2c3e50; margin: 2rem 0;'>🏛️ Destinasi Halaman {st.session_state.gallery_page_num}</h3>", unsafe_allow_html=True)
        
        # Display in grid (4 columns for gallery)
        cols_per_row = 4
        for i in range(0, len(page_destinations), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, destination in enumerate(page_destinations[i:i+cols_per_row]):
                if j < len(cols):
                    display_destination_card(destination, cols[j])
        
        # Bottom pagination
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Sebelumnya", key="bottom_prev", disabled=st.session_state.gallery_page_num <= 1):
                st.session_state.gallery_page_num -= 1
                st.rerun()
        
        with col2:
            # Page selector
            page_options = list(range(1, total_pages + 1))
            selected_page = st.selectbox(
                "Pilih halaman:",
                page_options,
                index=st.session_state.gallery_page_num - 1,
                key="page_selector"
            )
            if selected_page != st.session_state.gallery_page_num:
                st.session_state.gallery_page_num = selected_page
                st.rerun()
        
        with col3:
            if st.button("Selanjutnya ➡️", key="bottom_next", disabled=st.session_state.gallery_page_num >= total_pages):
                st.session_state.gallery_page_num += 1
                st.rerun()
                
    else:
        st.warning("🔍 Tidak ada destinasi ditemukan dengan kriteria yang dipilih.")
        
        # Show available stats
        st.markdown("### 📊 Statistik Dataset")
        cols = st.columns(len(INDONESIAN_CITIES))
        
        for i, (city, info) in enumerate(INDONESIAN_CITIES.items()):
            with cols[i]:
                st.metric(
                    label=f"🏙️ {city}",
                    value=f"{info['destinations']} destinasi",
                    delta=info['region']
                )

def main():
    """Main application with navigation"""
    
    # Initialize current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Beranda"
    
    # Navigation
    with st.container():
        # Get the current page index for option_menu
        current_index = 0 if st.session_state.current_page == "🏠 Beranda" else \
                       1 if st.session_state.current_page == "🔍 Cari Rekomendasi" else \
                       2 if st.session_state.current_page == "🖼️ Galeri" else 0
        
        selected = option_menu(
            menu_title=None,
            options=["🏠 Beranda", "🔍 Cari Rekomendasi", "🖼️ Galeri"],
            icons=["house", "search", "images"],
            menu_icon="cast",
            default_index=current_index,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#667eea", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "padding": "1rem", "border-radius": "10px"},
                "nav-link-selected": {"background-color": "#667eea", "color": "white"},
            }
        )
        
        # Update session state when menu is clicked
        if selected != st.session_state.current_page:
            st.session_state.current_page = selected
            st.rerun()
    
    # Page routing based on session state
    if st.session_state.current_page == "🏠 Beranda":
        homepage()
    elif st.session_state.current_page == "🔍 Cari Rekomendasi":
        recommendations_page()
    elif st.session_state.current_page == "🖼️ Galeri":
        gallery_page()
    
    # Footer with real data stats
    total_destinations = sum(city['destinations'] for city in INDONESIAN_CITIES.values())
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 0; margin-top: 4rem; border-top: 1px solid #e9ecef; color: #6c757d;">
        <p>🏝️ <strong>ExploreIndonesia</strong> - Jelajahi keindahan Nusantara dengan AI</p>
        <p style="font-size: 0.9rem;">📊 {total_destinations} destinasi di {len(INDONESIAN_CITIES)} kota | Dibuat dengan ❤️ untuk Indonesia</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()