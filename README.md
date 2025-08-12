# 🏝️ ExploreIndonesia - AI Tourism Recommendation Platform

![ExploreIndonesia](https://img.shields.io/badge/ExploreIndonesia-AI%20Tourism-blue?style=for-the-badge&logo=compass)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)

**ExploreIndonesia** adalah platform rekomendasi wisata Indonesia berbasis AI yang membantu pengguna menemukan destinasi wisata terbaik berdasarkan lokasi, preferensi, dan rating. Platform ini menggunakan machine learning untuk memberikan rekomendasi yang personal dan akurat dengan data real dari 437+ destinasi wisata Indonesia.

## ✨ Fitur Utama

### 🏠 **Halaman Beranda**
- **📍 GPS Detection** - Deteksi lokasi otomatis dengan status real-time & fallback ke Jakarta
- **🏙️ Dropdown Wilayah Real** - Pilih dari 5 kota dengan data aktual (Jakarta: 84, Yogyakarta: 126, Bandung: 124, dst)
- **🎯 Rekomendasi Populer** - 5 destinasi terbaik dengan rating 4.0+ dari dataset real
- **🖼️ Foto Asli** - Gambar destinasi hasil scraping dari folder `image/`
- **📱 Responsive Design** - UI/UX modern dengan gradient dan animasi

### 🔍 **Halaman Pencarian**
- **🎯 Advanced Filters** - Kota, kategori, rating, dan harga
- **📊 Customizable Results** - 5-20 hasil sesuai kebutuhan
- **🗂️ Grid Layout** - Tampilan kartu yang menarik
- **⚡ Real-time Search** - Hasil instan dengan API

### 🤖 **AI & ML Features**
- **Machine Learning Model** - Sistem rekomendasi berbasis scikit-learn
- **Content-Based Filtering** - Berdasarkan deskripsi dan kategori
- **Collaborative Filtering** - Berdasarkan rating pengguna lain
- **Location-Based Recommendation** - Menggunakan Haversine formula

## 🏗️ Arsitektur Sistem

```
ExploreIndonesia/
├── 🌐 Frontend (Streamlit)     # User Interface
│   ├── 🏠 Homepage            # GPS + Regional recommendations  
│   └── 🔍 Search Page         # Advanced search & filters
│
├── 🚀 Backend (FastAPI)       # REST API
│   ├── 🤖 ML Model           # Recommendation engine
│   ├── 📊 Data Processing     # Tourism data pipeline
│   └── 🔌 API Endpoints       # RESTful services
│
├── 🖼️ Image Storage           # 389MB+ foto real hasil scraping
└── 🐳 Docker Services         # Container orchestration
```

## 📊 Dataset & Model

### **Tourism Dataset Real**
- **437+ Destinasi** dari dataset `tourism_with_id.csv`
- **5 Kota Utama**: Jakarta (84), Yogyakarta (126), Bandung (124), Surabaya (46), Semarang (57)
- **Foto Real**: 389MB+ gambar hasil scraping per destinasi di folder `image/`
- **Rating Aktual**: Data rating dari wisatawan asli
- **Kategori Lengkap**: Budaya, Taman Hiburan, Cagar Alam, Bahari, Pusat Perbelanjaan, Tempat Ibadah
- **Harga Terstruktur**: Kategori murah (≤25k), menengah (25k-100k), mahal (>100k)

### **ML Model**
- **Algorithm**: Hybrid Recommendation System
- **Features**: TF-IDF, Rating, Price, Location, Category
- **Model File**: `recommendation_artifacts_optimal.pkl`
- **Accuracy**: Optimized untuk tourism domain Indonesia

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/ExploreIndonesia.git
cd ExploreIndonesia
```

### **2. Deploy dengan Docker (Recommended)**
```bash
# Build dan start semua services
docker-compose up --build -d

# Atau gunakan script deployment
./deploy.sh
```

### **3. Akses Application**
- **🌐 Website**: http://localhost:8501
- **🚀 API Docs**: http://localhost:8000/docs
- **📊 MLflow**: http://localhost:5000

### **4. Manual Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
cd api
uvicorn api:app --host 0.0.0.0 --port 8000

# Start web app (terminal baru)
cd website
streamlit run app.py --server.port 8501
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| **streamlit** | 8501 | Web frontend dengan Streamlit |
| **api** | 8000 | FastAPI backend dengan ML model |
| **mlflow** | 5000 | MLflow tracking server |

## 🔌 API Endpoints

### **🎯 Recommendations**
```http
GET /recommendations
```
**Parameters:**
- `location` - Filter berdasarkan kota
- `min_rating` - Rating minimal (3.0-5.0)
- `price_category` - murah/menengah/mahal
- `category` - Kategori wisata
- `top_n` - Jumlah hasil (1-50)

**Response:**
```json
[
  {
    "Place_Id": 1,
    "Place_Name": "Monas (Monumen Nasional)",
    "Description": "Monas adalah monumen bersejarah...",
    "Category": "Budaya",
    "City": "Jakarta",
    "Price": 15000,
    "Rating": 4.2,
    "score": 4.2,
    "price_category": "murah"
  }
]
```

### **📊 Statistics**
```http
GET /stats        # Dataset statistics
GET /cities       # Available cities
GET /categories   # Tourism categories
```

## 🏙️ Supported Cities (Real Data)

| Kota | Destinasi | Region | Koordinat | Status |
|------|-----------|--------|-----------|---------|
| **Jakarta** | 84 destinasi | DKI Jakarta | -6.175, 106.827 | ✅ Active |
| **Yogyakarta** | 126 destinasi | DI Yogyakarta | -7.801, 110.368 | ✅ Active |
| **Bandung** | 124 destinasi | Jawa Barat | -6.760, 107.610 | ✅ Active |
| **Surabaya** | 46 destinasi | Jawa Timur | -7.309, 112.822 | ✅ Active |
| **Semarang** | 57 destinasi | Jawa Tengah | -7.210, 110.342 | ✅ Active |

*Data destinasi berdasarkan analisis real dari `tourism_with_id.csv`*

## 🛠️ Tech Stack

### **Frontend**
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit) **Streamlit** - Web framework
- ![Python](https://img.shields.io/badge/Python-3776AB?logo=python) **streamlit-option-menu** - Navigation
- ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5) **Custom CSS/JS** - UI/UX enhancement

### **Backend**
- ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi) **FastAPI** - API framework
- ![Python](https://img.shields.io/badge/Python-3776AB?logo=python) **Pydantic** - Data validation
- ![Uvicorn](https://img.shields.io/badge/Uvicorn-4051B5?logo=uvicorn) **Uvicorn** - ASGI server

### **Machine Learning**
- ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn) **scikit-learn** - ML algorithms
- ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas) **Pandas** - Data processing
- ![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy) **NumPy** - Numerical computing
- **TF-IDF Vectorizer** - Text analysis

### **Infrastructure**
- ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker) **Docker & Docker Compose** - Containerization
- ![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow) **MLflow** - ML lifecycle management
- ![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx) **Nginx** - Reverse proxy (production)

## 📁 Project Structure

```
ExploreIndonesia/
├── 📱 website/              # Streamlit frontend
│   ├── app.py              # Main application
│   ├── Dockerfile          # Container config
│   ├── requirements.txt    # Python dependencies
│   └── 🖼️ image/          # Tourism photos (389MB)
│
├── 🚀 api/                 # FastAPI backend
│   ├── api.py             # Main API application
│   ├── Dockerfile         # Container config
│   ├── requirements.txt   # Python dependencies
│   └── 🤖 model/         # ML model artifacts
│
├── 📊 data/               # Raw datasets
│   ├── tourism_rating.csv
│   ├── tourism_with_id.csv
│   └── package_tourism.csv
│
├── 📓 notebooks/          # Jupyter notebooks
│   └── Model.ipynb       # ML model development
│
├── ⚙️ Configuration
│   ├── docker-compose.yml    # Multi-service orchestration
│   ├── docker-compose.prod.yml # Production config
│   ├── nginx.conf           # Nginx configuration
│   └── deploy.sh           # Deployment script
│
└── 📚 Documentation
    ├── README.md           # This file
    └── VPS_DEPLOYMENT.md   # VPS deployment guide
```

## 🌐 Deployment Options

### **1. Local Development**
```bash
docker-compose up --build
```

### **2. Production VPS**
```bash
# Copy docker-compose.prod.yml to server
docker-compose -f docker-compose.prod.yml up -d
```

### **3. Cloud Deployment**
- **AWS EC2** dengan Docker
- **Google Cloud Run** untuk serverless
- **DigitalOcean Droplets** dengan Docker Compose
- **Heroku** dengan container stack

## 🔧 Configuration

### **Environment Variables**
```env
# API Configuration
API_BASE_URL=http://api:8000  # Internal Docker network

# Streamlit Configuration  
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# MLflow Configuration
MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow/mlflow.db
```

### **Docker Compose Override**
Create `docker-compose.override.yml` for custom configurations:
```yaml
version: '3.3'
services:
  streamlit:
    ports:
      - "80:8501"  # Custom port mapping
    environment:
      - CUSTOM_ENV_VAR=value
```

## 📈 Performance & Monitoring

### **Application Metrics (Real Data)**
- **Response Time**: < 200ms untuk API calls dengan fallback system
- **Dataset Size**: 437+ destinasi real dari CSV analysis
- **Image Storage**: 389MB+ foto asli hasil scraping
- **Model Size**: ~50MB compressed dengan artifacts
- **Container Memory**: ~512MB per service
- **GPS Detection**: Real-time dengan fallback Jakarta

### **Health Checks & Status**
- ✅ **API Health**: `GET /` returns service status & ML model status
- ✅ **Model Fallback**: Dummy data system ketika ML model tidak tersedia  
- ✅ **Real Data**: Integration dengan `tourism_with_id.csv`
- ✅ **Docker Health**: Health checks configured untuk semua services
- ✅ **Image Loading**: Automatic fallback untuk missing images

## 🤝 Contributing

### **Development Setup**
1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make changes dan test
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

### **Code Style**
- Follow PEP 8 untuk Python code
- Use Black untuk code formatting
- Add type hints untuk functions
- Write docstrings untuk public methods

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Latest Updates & Improvements

### **✅ Production-Ready Features (Latest Release)**
- **🎯 Real GPS Detection**: Implementasi GPS dengan status real-time dan fallback system
- **📊 Data Integration**: Menggunakan dataset real `tourism_with_id.csv` dengan 437+ destinasi
- **🏙️ City Dropdown**: Data aktual per kota - Jakarta (84), Yogyakarta (126), Bandung (124), dll
- **🖼️ Image System**: Integrasi foto asli hasil scraping dari folder `image/` (389MB+)
- **🎨 UI/UX Modern**: Design production-ready dengan gradient, animasi, dan responsive layout
- **⚡ Fallback System**: Robust error handling dengan dummy data ketika ML model tidak tersedia
- **🐳 Docker Ready**: Full containerization dengan health checks dan monitoring

### **🔧 Technical Improvements**
- **Python 3.12**: Upgrade dari 3.10 untuk compatibility dengan dependencies terbaru
- **Real Data Analysis**: Analisis langsung dari CSV untuk statistik akurat
- **GPS Geolocation**: JavaScript-based detection dengan UI indicators
- **Image Handling**: Automatic path detection dan fallback system
- **API Robustness**: Complete error handling dan response validation

## 🙏 Acknowledgments

- **Indonesian Tourism Data** - Real dataset dari berbagai sumber terpercaya
- **Streamlit Community** - Framework web yang powerful untuk Python
- **FastAPI Team** - High-performance API framework dengan async support
- **scikit-learn** - Machine learning capabilities untuk recommendation engine
- **Docker Community** - Containerization technology untuk deployment
- **Indonesian Tourism Board** - Data dan informasi destinasi Indonesia

## 📞 Contact & Support

- **📧 Email**: your.email@domain.com
- **🐛 Issues**: [GitHub Issues](https://github.com/yourusername/ExploreIndonesia/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/yourusername/ExploreIndonesia/discussions)
- **📖 Documentation**: [Project Wiki](https://github.com/yourusername/ExploreIndonesia/wiki)

---

<div align="center">

**🏝️ Dibuat dengan ❤️ untuk Indonesia 🇮🇩**

*Jelajahi keindahan Nusantara dengan teknologi AI terdepan*

[![Stars](https://img.shields.io/github/stars/yourusername/ExploreIndonesia?style=social)](https://github.com/yourusername/ExploreIndonesia/stargazers)
[![Forks](https://img.shields.io/github/forks/yourusername/ExploreIndonesia?style=social)](https://github.com/yourusername/ExploreIndonesia/network/members)
[![Issues](https://img.shields.io/github/issues/yourusername/ExploreIndonesia)](https://github.com/yourusername/ExploreIndonesia/issues)
[![License](https://img.shields.io/github/license/yourusername/ExploreIndonesia)](https://github.com/yourusername/ExploreIndonesia/blob/main/LICENSE)

</div>