# ExploreIndonesia Website

Production-ready Streamlit web application for Indonesian tourism recommendations powered by AI.

## 🚀 Features

- **AI-Powered Recommendations**: Machine Learning based tourism recommendations
- **Advanced Filtering**: Filter by city, category, price, rating, and interests
- **Real-time Statistics**: Live data visualization and insights
- **Responsive Design**: Optimized for desktop and mobile
- **Content-based Search**: Search destinations by keywords and interests
- **Interactive UI**: Modern, clean interface with multi-page navigation

## 📋 Requirements

### API Backend
The website requires the FastAPI backend to be running:
```bash
cd api/
pip install -r requirements.txt
python api.py
```
API will be available at: `http://localhost:8000`

### Website Frontend
```bash
cd website/
pip install -r requirements.txt
streamlit run app.py
```
Website will be available at: `http://localhost:8501`

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Initial-Project
```

2. **Install API dependencies**
```bash
cd api/
pip install -r requirements.txt
```

3. **Install Website dependencies**
```bash
cd ../website/
pip install -r requirements.txt
```

4. **Run the API server**
```bash
cd ../api/
python api.py
```

5. **Run the Streamlit app** (in a new terminal)
```bash
cd website/
streamlit run app.py
```

## 📱 Usage

### Navigation
- **🏠 Beranda**: Overview with popular recommendations
- **🔍 Cari Wisata**: Advanced search with filters
- **📊 Statistik**: Platform statistics and insights  
- **ℹ️ Tentang**: Information about the platform

### Search Features
- **Location Filter**: Jakarta, Yogyakarta, Bandung, Semarang, Surabaya
- **Category Filter**: Budaya, Taman Hiburan, Cagar Alam, Bahari, etc.
- **Price Category**: murah, menengah, mahal
- **Rating Filter**: Minimum rating threshold
- **Interest Keywords**: Content-based filtering using keywords

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ Backend API (FastAPI) ←→ ML Model (LightGBM)
```

### API Endpoints Used
- `GET /recommendations` - Get tourism recommendations
- `GET /cities` - Get available cities
- `GET /categories` - Get available categories  
- `GET /stats` - Get platform statistics
- `GET /` - API health check

## 🎨 Design Features

- **Modern UI**: Gradient headers, cards, and responsive design
- **Custom CSS**: Styled components for better user experience
- **Interactive Charts**: Plotly visualizations for data insights
- **Loading States**: Spinners and progress indicators
- **Error Handling**: Graceful error messages and fallbacks

## ⚡ Performance

- **Caching**: API responses cached for 5-10 minutes
- **Lazy Loading**: Data loaded on demand
- **Session State**: Maintains search results across interactions
- **Optimized Queries**: Efficient API calls with parameters

## 🔧 Configuration

### API Configuration
Edit `API_BASE_URL` in `app.py`:
```python
API_BASE_URL = "http://localhost:8000"  # Change as needed
```

### Streamlit Configuration
Edit `.streamlit/config.toml` for theme and server settings.

## 📊 Data

The application works with 437+ tourism destinations across 5 major Indonesian cities:
- Jakarta (84 destinations)
- Yogyakarta (84 destinations)  
- Bandung, Semarang, Surabaya (remaining destinations)

## 🚀 Production Deployment

### Option 1: Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy with secrets for API URL

### Option 2: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Option 3: VPS/Cloud Server
1. Setup Python environment
2. Install dependencies
3. Run with process manager (PM2, systemd)
4. Setup reverse proxy (nginx)

## 🐛 Troubleshooting

### API Connection Issues
- Ensure FastAPI server is running on port 8000
- Check firewall settings
- Verify API_BASE_URL configuration

### Performance Issues
- Clear Streamlit cache: `st.cache_data.clear()`
- Reduce number of simultaneous requests
- Optimize API timeout settings

### Display Issues
- Clear browser cache
- Check CSS compatibility
- Verify Streamlit version compatibility

## 📈 Analytics

The app includes built-in analytics:
- API response times
- Search patterns
- Error tracking
- User interactions

## 🔮 Future Enhancements

- [ ] User authentication
- [ ] Favorite destinations
- [ ] Trip planning features
- [ ] Mobile app version
- [ ] Offline mode
- [ ] Multiple language support

## 📞 Support

For issues and support:
1. Check API server status
2. Review error logs
3. Test API endpoints directly
4. Contact development team

## 📄 License

This project is built for educational and demonstration purposes.