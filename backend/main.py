from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
import string
import random
from datetime import datetime
from typing import Optional
from database import SessionLocal, engine, Base, URLMapping
import re
import os

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
BASE_URL = "http://localhost:8000" if ENVIRONMENT == "development" else "https://s.casimirlundberg.fi"

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class URLCreate(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    created_at: datetime
    click_count: int
    expires_at: Optional[datetime] = None

class URLStats(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime

def generate_short_code(length: int = 6) -> str:
    """Generate a random short code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_custom_code(code: str) -> bool:
    """Validate custom code format"""
    return re.match(r'^[a-zA-Z0-9_-]+$', code) and len(code) <= 20

@app.post("/api/shorten", response_model=URLResponse)
async def shorten_url(url_data: URLCreate, db: Session = Depends(get_db)):
    """Create a shortened URL"""
    
    # Validate custom code if provided
    if url_data.custom_code:
        if not is_valid_custom_code(url_data.custom_code):
            raise HTTPException(status_code=400, detail="Invalid custom code format")
        
        # Check if custom code already exists
        existing = db.query(URLMapping).filter(URLMapping.short_code == url_data.custom_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom code already exists")
        
        short_code = url_data.custom_code
    else:
        # Generate unique short code
        while True:
            short_code = generate_short_code()
            existing = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
            if not existing:
                break
    
    # Create URL mapping
    url_mapping = URLMapping(
        original_url=str(url_data.url),
        short_code=short_code,
        expires_at=url_data.expires_at
    )
    
    db.add(url_mapping)
    db.commit()
    db.refresh(url_mapping)
    
    return URLResponse(
        id=url_mapping.id,
        original_url=url_mapping.original_url,
        short_code=url_mapping.short_code,
        short_url=f"{BASE_URL}/{url_mapping.short_code}",
        created_at=url_mapping.created_at,
        click_count=url_mapping.click_count,
        expires_at=url_mapping.expires_at
    )

@app.get("/{short_code}")
async def redirect_url(short_code: str, db: Session = Depends(get_db)):
    """Redirect to original URL and increment click count"""
    
    url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    # Check if URL has expired
    if url_mapping.expires_at and datetime.utcnow() > url_mapping.expires_at:
        raise HTTPException(status_code=410, detail="Short URL has expired")
    
    # Increment click count
    url_mapping.click_count += 1
    db.commit()
    
    return RedirectResponse(url=url_mapping.original_url)

@app.get("/api/stats/{short_code}", response_model=URLStats)
async def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    """Get statistics for a shortened URL"""
    
    url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return URLStats(
        short_code=url_mapping.short_code,
        original_url=url_mapping.original_url,
        click_count=url_mapping.click_count,
        created_at=url_mapping.created_at
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)