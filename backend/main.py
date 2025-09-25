from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.responses import RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, validator
import string
import random
from datetime import datetime, timedelta
from typing import Optional
from database import SessionLocal, engine, Base, URLMapping
import re
import os
import logging
from dotenv import load_dotenv

# Optional imports for production
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DOMAIN = os.getenv("DOMAIN", "coventure.es")

# Base URL - force localhost in development mode
if ENVIRONMENT == "development":
    BASE_URL = "http://localhost:8000"
else:
    BASE_URL = os.getenv("BASE_URL", f"https://{DOMAIN}")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
API_KEY = os.getenv("API_KEY", "default-api-key")
# CORS Origins - permissive in development, strict in production
if ENVIRONMENT == "development":
    ALLOWED_ORIGINS = ["*"]  # Allow all origins in development
else:
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", f"https://{DOMAIN},https://www.{DOMAIN}").split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Initialize Sentry for error tracking
if ENVIRONMENT == "production" and os.getenv("SENTRY_DSN") and SENTRY_AVAILABLE:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=0.1,
        environment=ENVIRONMENT,
    )

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Logging configuration
logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener", 
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Security middleware
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[DOMAIN, f"*.{DOMAIN}"]
    )

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"] if ENVIRONMENT == "development" else ["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Authentication dependency
def verify_api_key(x_api_key: str = Header(None)):
    if ENVIRONMENT == "production":
        if x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
    # In development mode, API key is optional
    return x_api_key

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
    
    @validator('url')
    def validate_url(cls, v):
        url_str = str(v)
        # Block localhost and internal IPs in production
        if ENVIRONMENT == "production":
            blocked_patterns = [
                r'localhost',
                r'127\.0\.0\.1',
                r'192\.168\.',
                r'10\.',
                r'172\.(1[6-9]|2[0-9]|3[01])\.',
                r'0\.0\.0\.0'
            ]
            for pattern in blocked_patterns:
                if re.search(pattern, url_str, re.IGNORECASE):
                    raise ValueError('Internal URLs are not allowed')
        
        # Ensure HTTPS in production
        if ENVIRONMENT == "production" and not url_str.startswith('https://'):
            raise ValueError('Only HTTPS URLs are allowed in production')
            
        return v
    
    @validator('custom_code')
    def validate_custom_code(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 20:
                raise ValueError('Custom code must be between 3 and 20 characters')
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Custom code can only contain letters, numbers, hyphens, and underscores')
        return v

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
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def shorten_url(
    request: Request,
    url_data: URLCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
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
@limiter.limit("100/minute")  # Higher limit for redirects
async def redirect_url(request: Request, short_code: str, db: Session = Depends(get_db)):
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
    
    return RedirectResponse(url=url_mapping.original_url, status_code=308)

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
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test"""
    try:
        # Test database connectivity
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

@app.get("/api/metrics")
async def metrics(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    """Basic metrics endpoint for monitoring"""
    try:
        total_urls = db.query(URLMapping).count()
        total_clicks = db.query(URLMapping).with_entities(
            db.func.sum(URLMapping.click_count)
        ).scalar() or 0
        
        # Recent activity (last 24 hours)
        recent_urls = db.query(URLMapping).filter(
            URLMapping.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count()
        
        return {
            "total_urls": total_urls,
            "total_clicks": total_clicks,
            "recent_urls_24h": recent_urls,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)