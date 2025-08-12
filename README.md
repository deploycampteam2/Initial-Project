# 🏝️ ExploreIndonesia - AI Tourism Recommendation Platform

![ExploreIndonesia](https://img.shields.io/badge/ExploreIndonesia-AI%20Tourism-blue?style=for-the-badge&logo=compass)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)

**ExploreIndonesia** adalah platform rekomendasi wisata Indonesia berbasis AI yang membantu pengguna menemukan destinasi wisata terbaik berdasarkan lokasi, preferensi, dan rating. Platform ini menggunakan machine learning untuk memberikan rekomendasi yang personal dan akurat.

## ✨ Fitur Utama

### 🏠 **Halaman Beranda**
- **📍 GPS Detection** - Deteksi lokasi otomatis dengan fallback ke Jakarta
- **🏙️ Dropdown Wilayah** - Pilih dari 12 kota besar Indonesia
- **🎯 Rekomendasi Populer** - 5 destinasi terbaik dengan rating 4.0+
- **📱 Responsive Design** - Optimal di semua perangkat

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
├── 🖼️ Image Storage           # 167 destinations × 5 photos
└── 🐳 Docker Services         # Container orchestration
```

## 📊 Dataset & Model

### **Tourism Dataset**
- **167 Destinasi** di 12 kota Indonesia
- **5 Foto** per destinasi (835+ gambar)
- **Rating & Review** dari wisatawan
- **Kategori Wisata**: Budaya, Taman Hiburan, Cagar Alam, Bahari, dll
- **Data Harga** dengan kategori: murah, menengah, mahal

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

## 🏙️ Supported Cities

| Kota | Region | Koordinat |
|------|--------|-----------|
| **Jakarta** | DKI Jakarta | -6.2088, 106.8456 |
| **Yogyakarta** | DI Yogyakarta | -7.7956, 110.3695 |
| **Bandung** | Jawa Barat | -6.9175, 107.6191 |
| **Surabaya** | Jawa Timur | -7.2504, 112.7688 |
| **Semarang** | Jawa Tengah | -6.9663, 110.4292 |
| **Malang** | Jawa Timur | -7.9797, 112.6304 |
| **Solo** | Jawa Tengah | -7.5755, 110.8243 |
| **Medan** | Sumatera Utara | 3.5952, 98.6722 |
| **Palembang** | Sumatera Selatan | -2.9761, 104.7754 |
| **Makassar** | Sulawesi Selatan | -5.1477, 119.4327 |
| **Denpasar** | Bali | -8.6705, 115.2126 |
| **Balikpapan** | Kalimantan Timur | -1.2379, 116.8529 |

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

### **Application Metrics**
- **Response Time**: < 200ms untuk API calls
- **Dataset Size**: 167 destinasi × 5 foto = 835+ images
- **Model Size**: ~50MB compressed
- **Container Memory**: ~512MB per service

### **Health Checks**
- API Health: `GET /` returns service status
- Model Status: `/stats` endpoint untuk ML model info
- Docker health checks configured untuk semua services

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

## 🙏 Acknowledgments

- **Indonesian Tourism Data** - Sourced from various public APIs
- **Streamlit Community** - For amazing web framework
- **FastAPI Team** - For high-performance API framework
- **scikit-learn** - For machine learning capabilities
- **Indonesian Tourism Board** - For destination information

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