from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, date
from pydantic import BaseModel

app = FastAPI(
    title="ExploreIndonesia API",
    description="API untuk rekomendasi destinasi wisata Indonesia",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {
        "message": "Welcome to ExploreIndonesia API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/destinations", response_model=List[Destination])
async def get_destinations(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[List[str]] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum rating"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Limit results")
):
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

@app.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[List[str]] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(5, ge=1, le=20, description="Number of recommendations")
):
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
    df = load_tourism_data()
    
    return {
        "total_destinations": df['Destination'].nunique(),
        "total_visitors": int(df['Visitors'].sum()),
        "avg_rating": round(df['Rating'].mean(), 2),
        "total_reviews": int(df['Reviews'].sum()),
        "regions": df['Region'].unique().tolist(),
        "categories": df['Category'].unique().tolist()
    }

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