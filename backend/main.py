from fastapi import FastAPI, HTTPException, Depends, Request, Header, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, HttpUrl, validator, EmailStr
import string
import random
from datetime import datetime, timedelta
from typing import Optional
from database import SessionLocal, engine, Base, URLMapping, User
from auth import verify_password, get_password_hash, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
import re
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DOMAIN = os.getenv("DOMAIN", "coventure.es")
BASE_URL = ("http://localhost:8000" if ENVIRONMENT == "development" 
           else os.getenv("BASE_URL", f"https://{DOMAIN}"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
API_KEY = os.getenv("API_KEY", "default-api-key")
ALLOWED_ORIGINS = (["*"] if ENVIRONMENT == "development" 
                  else os.getenv("ALLOWED_ORIGINS", f"https://{DOMAIN},https://www.{DOMAIN}").split(","))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

logging.basicConfig(
    level=logging.INFO if ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="URL Changer", 
    description="A professional URL changing service",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Failed to initialize database after all retries")
                # Don't raise the exception - let the app start anyway
                # The health endpoint and individual requests will handle DB errors
            else:
                import asyncio
                await asyncio.sleep(retry_delay)

if ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[DOMAIN, f"*.{DOMAIN}"])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"] if ENVIRONMENT == "development" else ["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(None)):
    if ENVIRONMENT == "production" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get the current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Ensure the current user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Admin access required"
        )
    return current_user

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password (case-insensitive)"""
    user = db.query(User).filter(func.lower(User.username) == username.lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

class URLCreate(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('url')
    def validate_url(cls, v):
        url_str = str(v)
        if ENVIRONMENT == "production":
            blocked_patterns = [
                r'localhost', r'127\.0\.0\.1', r'192\.168\.', r'10\.',
                r'172\.(1[6-9]|2[0-9]|3[01])\.', r'0\.0\.0\.0'
            ]
            for pattern in blocked_patterns:
                if re.search(pattern, url_str, re.IGNORECASE):
                    raise ValueError('Internal URLs are not allowed')
            
            if not url_str.startswith('https://'):
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

# Authentication Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_custom_code(code: str) -> bool:
    return re.match(r'^[a-zA-Z0-9_-]+$', code) and len(code) <= 20

# Authentication Endpoints
@app.post("/api/register", response_model=UserResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists (case-insensitive)
    if db.query(User).filter(func.lower(User.username) == user_data.username.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists (case-insensitive)
    if db.query(User).filter(func.lower(User.email) == user_data.email.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user (store username and email in lowercase)
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"New user registered: {user.username}")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at
    )

@app.post("/api/login", response_model=Token)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    user = authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )

@app.get("/api/my-urls", response_model=list[URLResponse])
async def get_my_urls(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all URLs for the current user"""
    urls = db.query(URLMapping).filter(URLMapping.user_id == current_user.id).order_by(URLMapping.created_at.desc()).all()
    
    return [URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{BASE_URL}/{url.short_code}",
        created_at=url.created_at,
        click_count=url.click_count,
        expires_at=url.expires_at
    ) for url in urls]

@app.post("/api/shorten", response_model=URLResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def shorten_url(
    request: Request,
    url_data: URLCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if url_data.custom_code:
        if not is_valid_custom_code(url_data.custom_code):
            raise HTTPException(status_code=400, detail="Invalid custom code format")
        
        existing = db.query(URLMapping).filter(URLMapping.short_code == url_data.custom_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Custom code already exists")
        
        short_code = url_data.custom_code
    else:
        while True:
            short_code = generate_short_code()
            existing = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
            if not existing:
                break
    
    url_mapping = URLMapping(
        original_url=str(url_data.url),
        short_code=short_code,
        expires_at=url_data.expires_at,
        user_id=current_user.id
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
@limiter.limit("100/minute")
async def redirect_url(request: Request, short_code: str, db: Session = Depends(get_db)):
    url_mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    if url_mapping.expires_at and datetime.utcnow() > url_mapping.expires_at:
        raise HTTPException(status_code=410, detail="Short URL has expired")
    
    url_mapping.click_count += 1
    db.commit()
    
    return RedirectResponse(url=url_mapping.original_url, status_code=308)

@app.get("/api/stats/{short_code}", response_model=URLStats)
async def get_url_stats(short_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    url_mapping = db.query(URLMapping).filter(
        URLMapping.short_code == short_code,
        URLMapping.user_id == current_user.id
    ).first()
    
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found or not authorized")
    
    return URLStats(
        short_code=url_mapping.short_code,
        original_url=url_mapping.original_url,
        click_count=url_mapping.click_count,
        created_at=url_mapping.created_at
    )

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connectivity by querying the URL mappings table
        result = db.query(URLMapping).first()
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
    try:
        total_urls = db.query(URLMapping).count()
        total_clicks = db.query(URLMapping).with_entities(
            func.sum(URLMapping.click_count)
        ).scalar() or 0
        
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

@app.delete("/api/urls/{short_code}")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def delete_url(
    request: Request,
    short_code: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a URL mapping by short code"""
    url_mapping = db.query(URLMapping).filter(
        URLMapping.short_code == short_code,
        URLMapping.user_id == current_user.id
    ).first()
    
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found or not authorized")
    
    try:
        db.delete(url_mapping)
        db.commit()
        logger.info(f"Deleted URL mapping: {short_code} by user: {current_user.username}")
        return {"message": f"URL '{short_code}' deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete URL mapping {short_code}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete URL")

# Admin endpoints
@app.post("/api/admin/users", response_model=UserResponse)
async def create_user(
    user_data: AdminUserCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if user already exists (case-insensitive username check)
    existing_user = db.query(User).filter(
        (func.lower(User.username) == user_data.username.lower()) | 
        (func.lower(User.email) == user_data.email.lower())
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="User with this username or email already exists"
        )
    
    # Create new user (store username in lowercase)
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=hashed_password,
        is_admin=user_data.is_admin,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Admin {admin_user.username} created user: {new_user.username}")
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        is_admin=new_user.is_admin,
        created_at=new_user.created_at
    )

@app.get("/api/admin/users", response_model=list[UserResponse])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at
    ) for user in users]

@app.get("/api/admin/urls", response_model=list[URLResponse])
async def get_all_urls(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all URLs from all users (admin only)"""
    urls = db.query(URLMapping).order_by(URLMapping.created_at.desc()).all()
    
    return [URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{BASE_URL}/{url.short_code}",
        created_at=url.created_at,
        click_count=url.click_count,
        expires_at=url.expires_at
    ) for url in urls]

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user and all their URLs (admin only)"""
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Delete all URLs belonging to the user
        db.query(URLMapping).filter(URLMapping.user_id == user_id).delete()
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        logger.info(f"Admin {admin_user.username} deleted user: {user.username}")
        return {"message": f"User '{user.username}' and all associated URLs deleted successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Mount static files at the end so they don't interfere with API routes
if ENVIRONMENT == "production" and os.path.exists("/app/static"):
    app.mount("/", StaticFiles(directory="/app/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)