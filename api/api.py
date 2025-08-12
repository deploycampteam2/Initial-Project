from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, date
from pydantic import BaseModel
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(
    title="ExploreIndonesia API",
    description="API untuk rekomendasi destinasi wisata Indonesia dengan ML",
    version="1.0.0"
)

# Global variables untuk model dan data
model_artifacts = None
loaded = False

class Destination(BaseModel):
    destination: str
    region: str
    category: str
    visitors: int
    rating: float
    reviews: int
    budget_min: int
    budget_max: int
    date: str

class RecommendationResponse(BaseModel):
    destination: str
    region: str
    category: str
    rating: float
    reviews: int
    visitors: int
    budget_min: int
    budget_max: int
    score: float

class TourismRecommendationResponse(BaseModel):
    Place_Id: int
    Place_Name: str
    Description: str
    Category: str
    City: str
    Price: int
    Rating: float
    score: float
    price_category: str

class RecommendationRequest(BaseModel):
    location: Optional[str] = None
    min_rating: Optional[float] = None
    price_category: Optional[str] = None
    category: Optional[str] = None
    interests: Optional[List[str]] = None  # Keyword interests for content-based filtering
    top_n: int = 10

def load_ml_model():
    """Load the ML model and artifacts"""
    global model_artifacts, loaded
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), "model", "recommendation_artifacts_optimal.pkl")
        
        if not os.path.exists(model_path):
            print(f"Model file not found at: {model_path}")
            return False
            
        with open(model_path, "rb") as f:
            model_artifacts = pickle.load(f)
        
        loaded = True
        print("ML model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading ML model: {e}")
        return False

def create_feature_matrix_for_user(user_id, places_list, artifacts):
    """Create feature matrix for a specific user and places"""
    places_df = artifacts["places_df"]
    users_df = artifacts["users_df"]
    
    if user_id not in users_df['User_Id'].values:
        return None, None
    
    user_age = users_df[users_df['User_Id'] == user_id]['Age'].iloc[0]
    places_indexed = places_df.set_index('Place_Id')
    
    # Create TF-IDF features (simplified for API)
    tfidf = TfidfVectorizer(max_features=100)
    tfidf_matrix = tfidf.fit_transform(places_df['Description'].fillna(""))
    
    # Mock content scores and collaborative filtering scores for API usage
    feature_rows = []
    for p_id in places_list:
        if p_id in places_indexed.index:
            place_features = places_indexed.loc[p_id]
            
            # Simple feature engineering for API
            price_bins = [-1, 25000, 100000, np.inf]
            price_labels = ['murah', 'menengah', 'mahal']
            price_cat = pd.cut([place_features['Price']], bins=price_bins, labels=price_labels)[0]
            
            age_price_feature = 1.0  # Default interaction
            if user_age < 25 and price_cat == 'mahal':
                age_price_feature = 0.0
            elif user_age > 40 and price_cat == 'murah':
                age_price_feature = 0.5
            
            features = [
                0.5,  # content_score (mock)
                0.5,  # user_cf_score (mock)  
                0.5,  # item_cf_score (mock)
                user_age,
                place_features['Rating'],
                place_features['Price'],
                place_features['Category'],
                place_features['City'],
                age_price_feature
            ]
            feature_rows.append(features)
    
    return np.array(feature_rows), places_list

def recommend_places_general(location=None, min_rating=None, price_cat=None, category_name=None, interests=None, top_n=10):
    """General recommendation system without user dependency"""
    global model_artifacts, loaded
    
    if not loaded or model_artifacts is None:
        return []
    
    try:
        places_df = model_artifacts["places_df"].copy()
        
        # Apply basic filters
        if location:
            places_df = places_df[places_df['City_name'] == location]
        if min_rating is not None:
            places_df = places_df[places_df['Rating'] >= min_rating]
        if price_cat is not None:
            places_df = places_df[places_df['price_category'] == price_cat]
        if category_name is not None:
            places_df = places_df[places_df['Category_name'] == category_name]
        
        if places_df.empty:
            return []
        
        # Content-based filtering if interests are provided
        if interests and len(interests) > 0:
            places_df = content_based_filtering(places_df, interests)
        
        # Calculate composite score: Rating + Popularity + Content similarity (if applicable)
        places_df['popularity_score'] = places_df['Rating'] / 5.0  # Normalize rating to 0-1
        
        # Add price preference score (cheaper places get higher score for general users)
        price_score_map = {'murah': 1.0, 'menengah': 0.7, 'mahal': 0.4}
        places_df['price_score'] = places_df['price_category'].map(price_score_map).fillna(0.5)
        
        # Final composite score
        places_df['final_score'] = (
            places_df['popularity_score'] * 0.6 +  # Rating weight
            places_df['price_score'] * 0.2 +       # Price preference weight
            places_df.get('content_score', 0) * 0.2  # Content similarity weight (if available)
        )
        
        # Sort and return top N
        result = places_df.nlargest(top_n, 'final_score')
        result['score'] = result['final_score']
        
        return result.to_dict('records')
        
    except Exception as e:
        print(f"Error in general recommendation: {e}")
        # Fallback to simple rating-based recommendation
        return recommend_popular_places(location, min_rating, price_cat, category_name, top_n)

def content_based_filtering(places_df, interests):
    """Filter places based on content similarity with user interests"""
    try:
        # Combine interests into a single query
        user_query = " ".join(interests).lower()
        
        # Create TF-IDF vectorizer
        tfidf = TfidfVectorizer(max_features=500, stop_words=None)
        
        # Prepare descriptions for TF-IDF
        descriptions = places_df['Description'].fillna("").str.lower()
        all_texts = descriptions.tolist() + [user_query]
        
        # Fit TF-IDF and calculate similarities
        tfidf_matrix = tfidf.fit_transform(all_texts)
        
        # Calculate cosine similarity between user query and all places
        user_tfidf = tfidf_matrix[-1:]  # Last item is user query
        place_tfidf = tfidf_matrix[:-1]  # All except last are place descriptions
        
        similarities = cosine_similarity(user_tfidf, place_tfidf).flatten()
        
        # Add content score to DataFrame
        places_df = places_df.copy()
        places_df['content_score'] = similarities
        
        # Filter places with similarity above threshold
        threshold = 0.1
        places_df = places_df[places_df['content_score'] >= threshold]
        
        return places_df
        
    except Exception as e:
        print(f"Error in content-based filtering: {e}")
        # Return original dataframe if content filtering fails
        places_df['content_score'] = 0.5  # Neutral score
        return places_df

def recommend_popular_places(user_location=None, min_rating=None, price_cat=None, category_name=None, top_n=10):
    """Fallback recommendation based on popularity"""
    global model_artifacts
    
    if model_artifacts is None:
        return []
    
    places_df = model_artifacts["places_df"]
    candidate_places = places_df.copy()
    
    # Apply filters
    if user_location:
        candidate_places = candidate_places[candidate_places['City_name'] == user_location]
    if min_rating is not None:
        candidate_places = candidate_places[candidate_places['Rating'] >= min_rating]
    if price_cat is not None:
        candidate_places = candidate_places[candidate_places['price_category'] == price_cat]
    if category_name is not None:
        candidate_places = candidate_places[candidate_places['Category_name'] == category_name]
    
    if candidate_places.empty:
        return []
    
    # Sort by rating and return top N
    results = candidate_places.sort_values('Rating', ascending=False).head(top_n)
    
    # Add mock score
    results['score'] = results['Rating']
    
    return results.to_dict('records')

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
    
    dates = pd.date_range('2024-11-01', periods=30)
    
    data = []
    for date in dates:
        for i, dest in enumerate(destinations):
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
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

def get_fallback_recommendations(location=None, min_rating=None, price_category=None, category=None, top_n=10):
    """Fallback recommendations using dummy data when ML model is not available"""
    dummy_places = [
        {
            "Place_Id": 1,
            "Place_Name": "Monas (Monumen Nasional)",
            "Description": "Monas adalah monumen bersejarah setinggi 132 meter yang menjadi simbol Jakarta dan Indonesia.",
            "Category": "Budaya",
            "City": "Jakarta", 
            "Price": 15000,
            "Rating": 4.2,
            "price_category": "murah"
        },
        {
            "Place_Id": 2,
            "Place_Name": "Candi Borobudur",
            "Description": "Candi Buddha terbesar di dunia yang merupakan warisan budaya UNESCO.",
            "Category": "Budaya",
            "City": "Yogyakarta",
            "Price": 50000,
            "Rating": 4.8,
            "price_category": "menengah"
        },
        {
            "Place_Id": 3,
            "Place_Name": "Pantai Kuta",
            "Description": "Pantai yang terkenal dengan ombaknya yang bagus untuk surfing dan sunset yang indah.",
            "Category": "Bahari",
            "City": "Bandung",
            "Price": 0,
            "Rating": 4.5,
            "price_category": "murah"
        },
        {
            "Place_Id": 4,
            "Place_Name": "Taman Mini Indonesia Indah",
            "Description": "Taman budaya yang menampilkan keragaman budaya Indonesia dalam satu lokasi.",
            "Category": "Taman Hiburan",
            "City": "Jakarta",
            "Price": 25000,
            "Rating": 4.1,
            "price_category": "murah"
        },
        {
            "Place_Id": 5,
            "Place_Name": "Malioboro Street",
            "Description": "Jalan legendaris di Yogyakarta dengan berbagai toko, kuliner, dan budaya lokal.",
            "Category": "Pusat Perbelanjaan",
            "City": "Yogyakarta",
            "Price": 0,
            "Rating": 4.4,
            "price_category": "murah"
        }
    ]
    
    # Apply filters
    filtered_places = dummy_places.copy()
    
    if location:
        filtered_places = [p for p in filtered_places if p["City"] == location]
    if min_rating is not None:
        filtered_places = [p for p in filtered_places if p["Rating"] >= min_rating]
    if price_category:
        filtered_places = [p for p in filtered_places if p["price_category"] == price_category]
    if category:
        filtered_places = [p for p in filtered_places if p["Category"] == category]
    
    # Add score and limit results
    for place in filtered_places:
        place["score"] = place["Rating"]
    
    return filtered_places[:top_n]

@app.on_event("startup")
async def startup_event():
    """Load ML model on startup"""
    try:
        load_ml_model()
    except Exception as e:
        print(f"Failed to load ML model: {e}")
        print("Running in fallback mode with dummy data")

@app.get("/")
async def root():
    return {
        "message": "Welcome to ExploreIndonesia API with ML Recommendation",
        "version": "1.0.0",
        "docs": "/docs",
        "ml_model_loaded": loaded
    }

@app.get("/recommendations", response_model=List[TourismRecommendationResponse])
async def get_recommendations(
    location: Optional[str] = Query(None, description="Filter berdasarkan kota (Jakarta, Yogyakarta, Bandung, Semarang, Surabaya)"),
    min_rating: Optional[float] = Query(None, ge=3.0, le=5.0, description="Rating minimal"),
    price_category: Optional[str] = Query(None, description="Kategori harga (murah/menengah/mahal)"),
    category: Optional[str] = Query(None, description="Kategori wisata (Budaya, Taman Hiburan, Cagar Alam, Bahari, Pusat Perbelanjaan, Tempat Ibadah)"),
    interests: Optional[str] = Query(None, description="Minat/kata kunci yang dicari (pisahkan dengan koma)"),
    top_n: int = Query(10, ge=1, le=50, description="Jumlah rekomendasi")
):
    """
    Endpoint untuk mendapatkan rekomendasi wisata general (tanpa user_id)
    """
    if not loaded:
        # Fallback to dummy data
        print("Model not loaded, using fallback data")
        return get_fallback_recommendations(location, min_rating, price_category, category, top_n)
    
    try:
        # Parse interests from string to list
        interest_list = None
        if interests:
            interest_list = [i.strip() for i in interests.split(',') if i.strip()]
        
        recommendations = recommend_places_general(
            location=location,
            min_rating=min_rating,
            price_cat=price_category,
            category_name=category,
            interests=interest_list,
            top_n=top_n
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="Tidak ada rekomendasi yang ditemukan dengan kriteria tersebut")
        
        # Convert to response model
        response = []
        for rec in recommendations:
            response.append(TourismRecommendationResponse(
                Place_Id=rec['Place_Id'],
                Place_Name=rec['Place_Name'],
                Description=rec['Description'][:200] + "..." if len(rec['Description']) > 200 else rec['Description'],
                Category=rec['Category_name'],
                City=rec['City_name'],
                Price=rec['Price'],
                Rating=rec['Rating'],
                score=float(rec['score']),
                price_category=rec['price_category']
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/recommendations", response_model=List[TourismRecommendationResponse])
async def post_recommendations(request: RecommendationRequest):
    """
    Endpoint POST untuk mendapatkan rekomendasi wisata general
    """
    if not loaded:
        # Fallback to dummy data
        print("Model not loaded, using fallback data")
        return get_fallback_recommendations(request.location, request.min_rating, request.price_category, request.category, request.top_n)
    
    try:
        recommendations = recommend_places_general(
            location=request.location,
            min_rating=request.min_rating,
            price_cat=request.price_category,
            category_name=request.category,
            interests=request.interests,
            top_n=request.top_n
        )
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="Tidak ada rekomendasi yang ditemukan dengan kriteria tersebut")
        
        # Convert to response model
        response = []
        for rec in recommendations:
            response.append(TourismRecommendationResponse(
                Place_Id=rec['Place_Id'],
                Place_Name=rec['Place_Name'],
                Description=rec['Description'][:200] + "..." if len(rec['Description']) > 200 else rec['Description'],
                Category=rec['Category_name'],
                City=rec['City_name'],
                Price=rec['Price'],
                Rating=rec['Rating'],
                score=float(rec['score']),
                price_category=rec['price_category']
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/places")
async def get_places(
    city: Optional[str] = Query(None, description="Filter berdasarkan kota"),
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    limit: int = Query(20, ge=1, le=100, description="Batasi hasil")
):
    """
    Endpoint untuk mendapatkan daftar tempat wisata
    """
    if not loaded or model_artifacts is None:
        raise HTTPException(status_code=503, detail="Data belum dimuat")
    
    places_df = model_artifacts["places_df"]
    
    if city:
        places_df = places_df[places_df['City_name'] == city]
    if category:
        places_df = places_df[places_df['Category_name'] == category]
    
    places_df = places_df.head(limit)
    
    return places_df.to_dict('records')

@app.get("/destinations", response_model=List[Destination])
async def get_destinations(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[List[str]] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum rating"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Limit results")
):
    """
    Legacy endpoint untuk kompatibilitas (menggunakan data dummy)
    """
    df = load_tourism_data()
    
    if region:
        df = df[df['Region'] == region]
    
    if category:
        df = df[df['Category'].isin(category)]
    
    if min_rating:
        df = df[df['Rating'] >= min_rating]
    
    df = df.head(limit)
    
    destinations = []
    for _, row in df.iterrows():
        destinations.append(Destination(
            destination=row['Destination'],
            region=row['Region'],
            category=row['Category'],
            visitors=int(row['Visitors']),
            rating=float(row['Rating']),
            reviews=int(row['Reviews']),
            budget_min=int(row['Budget_Min']),
            budget_max=int(row['Budget_Max']),
            date=row['Date']
        ))
    
    return destinations

@app.get("/legacy-recommendations", response_model=List[RecommendationResponse])
async def get_legacy_recommendations(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[List[str]] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(5, ge=1, le=20, description="Number of recommendations")
):
    """
    Legacy endpoint untuk kompatibilitas (menggunakan data dummy)
    """
    df = load_tourism_data()
    
    if region:
        df = df[df['Region'] == region]
    
    if category:
        df = df[df['Category'].isin(category)]
    
    top_destinations = df.groupby('Destination').agg({
        'Rating': 'mean',
        'Visitors': 'sum',
        'Reviews': 'sum',
        'Region': 'first',
        'Category': 'first',
        'Budget_Min': 'mean',
        'Budget_Max': 'mean'
    }).reset_index()
    
    top_destinations['Score'] = (
        top_destinations['Rating'] * 0.4 + 
        (top_destinations['Visitors'] / top_destinations['Visitors'].max()) * 5 * 0.3 +
        (top_destinations['Reviews'] / top_destinations['Reviews'].max()) * 5 * 0.3
    )
    
    top_destinations = top_destinations.sort_values('Score', ascending=False).head(limit)
    
    recommendations = []
    for _, row in top_destinations.iterrows():
        recommendations.append(RecommendationResponse(
            destination=row['Destination'],
            region=row['Region'],
            category=row['Category'],
            rating=float(row['Rating']),
            reviews=int(row['Reviews']),
            visitors=int(row['Visitors']),
            budget_min=int(row['Budget_Min']),
            budget_max=int(row['Budget_Max']),
            score=float(row['Score'])
        ))
    
    return recommendations

@app.get("/stats")
async def get_stats():
    """
    Get statistics from real tourism data
    """
    if not loaded or model_artifacts is None:
        # Fallback to dummy data
        df = load_tourism_data()
        return {
            "total_destinations": df['Destination'].nunique(),
            "total_visitors": int(df['Visitors'].sum()),
            "avg_rating": round(df['Rating'].mean(), 2),
            "total_reviews": int(df['Reviews'].sum()),
            "regions": df['Region'].unique().tolist(),
            "categories": df['Category'].unique().tolist(),
            "data_source": "dummy"
        }
    
    places_df = model_artifacts["places_df"]
    
    return {
        "total_destinations": len(places_df),
        "avg_rating": round(places_df['Rating'].mean(), 2),
        "cities": places_df['City_name'].unique().tolist(),
        "categories": places_df['Category_name'].unique().tolist(),
        "price_categories": places_df['price_category'].value_counts().to_dict(),
        "rating_distribution": places_df['Rating'].describe().to_dict(),
        "data_source": "ml_model"
    }

@app.get("/cities")
async def get_cities():
    """
    Get available cities
    """
    if not loaded or model_artifacts is None:
        return ["Jakarta", "Yogyakarta", "Bandung", "Semarang", "Surabaya"]
    
    places_df = model_artifacts["places_df"]
    return places_df['City_name'].unique().tolist()

@app.get("/categories")
async def get_categories():
    """
    Get available tourism categories
    """
    if not loaded or model_artifacts is None:
        return ["Budaya", "Taman Hiburan", "Cagar Alam", "Bahari", "Pusat Perbelanjaan", "Tempat Ibadah"]
    
    places_df = model_artifacts["places_df"]
    return places_df['Category_name'].unique().tolist()

@app.get("/regions")
async def get_regions():
    df = load_tourism_data()
    region_stats = df.groupby('Region').agg({
        'Visitors': 'sum',
        'Rating': 'mean',
        'Destination': 'nunique'
    }).reset_index()
    
    regions = []
    for _, row in region_stats.iterrows():
        regions.append({
            "region": row['Region'],
            "total_visitors": int(row['Visitors']),
            "avg_rating": round(row['Rating'], 2),
            "destinations_count": int(row['Destination'])
        })
    
    return regions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)