#!/usr/bin/env python3
"""
Test script untuk mengecek responsivitas carousel
"""

import sys
import os
import streamlit as st
from PIL import Image

# Add the current directory to path to import app
sys.path.append(os.path.dirname(__file__))

def test_carousel_functionality():
    """Test basic carousel functionality"""
    
    st.title("🧪 Test Carousel Responsivitas")
    
    # Test mobile detection
    st.subheader("1. Mobile Detection Test")
    mobile_detection_js = """
    <script>
    function detectMobile() {
        const isMobile = window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        document.getElementById('mobile-status').innerHTML = isMobile ? '📱 Mobile View Detected' : '🖥️ Desktop View Detected';
        document.getElementById('viewport-info').innerHTML = `Viewport: ${window.innerWidth}x${window.innerHeight}`;
    }
    
    detectMobile();
    window.addEventListener('resize', detectMobile);
    </script>
    <div id="mobile-status" style="padding: 1rem; background: #e3f2fd; border-radius: 8px; margin: 1rem 0;"></div>
    <div id="viewport-info" style="padding: 0.5rem; background: #f5f5f5; border-radius: 4px; font-family: monospace;"></div>
    """
    
    st.components.v1.html(mobile_detection_js, height=150)
    
    # Display current session state
    st.subheader("2. Session State Test")
    st.write("Mobile view in session state:", st.session_state.get('mobile_view', 'Not detected'))
    
    # Test image resizing
    st.subheader("3. Image Resize Test")
    
    # Create test images for different scenarios
    test_scenarios = [
        {"name": "Desktop (400x200)", "width": 400, "height": 200, "mobile": False},
        {"name": "Mobile (300x150)", "width": 300, "height": 150, "mobile": True},
        {"name": "Small Mobile (250x120)", "width": 250, "height": 120, "mobile": True}
    ]
    
    # Show different image sizes
    cols = st.columns(len(test_scenarios))
    for i, scenario in enumerate(test_scenarios):
        with cols[i]:
            st.write(f"**{scenario['name']}**")
            # Create a test image using PIL
            try:
                test_img = Image.new('RGB', (scenario['width'], scenario['height']), color='#667eea')
                st.image(test_img, caption=f"{scenario['width']}x{scenario['height']}", use_container_width=True)
            except Exception as e:
                st.error(f"Error creating test image: {e}")
    
    # Test carousel navigation
    st.subheader("4. Carousel Navigation Test")
    
    # Simple carousel simulation
    carousel_key = "test_carousel"
    if carousel_key not in st.session_state:
        st.session_state[carousel_key] = 0
    
    test_images = [f"Test Image {i+1}" for i in range(3)]
    current_idx = st.session_state[carousel_key]
    
    # Display current "image"
    st.info(f"Current Image: {test_images[current_idx]} ({current_idx + 1}/{len(test_images)})")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️", key="test_prev"):
            st.session_state[carousel_key] = (current_idx - 1) % len(test_images)
            st.rerun()
    
    with col2:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>{current_idx + 1} / {len(test_images)}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("➡️", key="test_next"):
            st.session_state[carousel_key] = (current_idx + 1) % len(test_images)
            st.rerun()
    
    # CSS test
    st.subheader("5. CSS Responsiveness Test")
    
    responsive_test_css = """
    <style>
    .test-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        .test-container {
            padding: 1rem;
            font-size: 0.9rem;
        }
    }
    
    @media (max-width: 480px) {
        .test-container {
            padding: 0.8rem;
            font-size: 0.8rem;
        }
    }
    
    .test-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .test-item {
        background: #f0f0f0;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    @media (max-width: 768px) {
        .test-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    
    <div class="test-container">
        <h3>Responsive CSS Test</h3>
        <p>This container should adapt to screen size</p>
    </div>
    
    <div class="test-grid">
        <div class="test-item">Item 1</div>
        <div class="test-item">Item 2</div>
        <div class="test-item">Item 3</div>
        <div class="test-item">Item 4</div>
    </div>
    """
    
    st.markdown(responsive_test_css, unsafe_allow_html=True)
    
    # Performance test
    st.subheader("6. Performance Information")
    
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        st.metric("CPU Usage", f"{cpu_percent}%")
        st.metric("Memory Usage", f"{memory_info.percent}%")
    except ImportError:
        st.info("Install psutil for performance monitoring: pip install psutil")
    
    # Instructions
    st.subheader("📋 Test Instructions")
    st.markdown("""
    **Untuk menguji responsivitas:**
    
    1. **Desktop Testing:**
       - Buka aplikasi di browser desktop
       - Resize window browser dari lebar ke sempit
       - Perhatikan perubahan layout dan ukuran gambar
    
    2. **Mobile Testing:**
       - Buka aplikasi di smartphone
       - Atau gunakan Developer Tools browser (F12) dan pilih mobile view
       - Test portrait dan landscape orientation
    
    3. **Carousel Testing:**
       - Test navigasi carousel dengan tombol panah
       - Pastikan gambar ter-resize dengan benar
       - Periksa smooth transitions
    
    4. **Performance Testing:**
       - Monitor loading time untuk gambar
       - Test dengan koneksi internet lambat
       - Pastikan tidak ada memory leaks
    """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Carousel Responsiveness Test",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    test_carousel_functionality()