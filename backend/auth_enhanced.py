"""
Enhanced authentication with security features
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
import bcrypt
import os
import logging
import hashlib
import secrets
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration with better defaults
SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "change-this-in-production"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))

# Security: Track failed login attempts
failed_login_attempts: Dict[str, Dict[str, Any]] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

def is_strong_password(password: str) -> tuple[bool, str]:
    """Check password strength"""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    checks = {
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password), 
        'digits': any(c.isdigit() for c in password),
        'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    }
    
    missing = [check for check, passed in checks.items() if not passed]
    
    if len(missing) > 1:  # Allow missing one requirement
        return False, f"Password must include: {', '.join(missing)}"
    
    # Check for common weak passwords
    weak_patterns = ['123456', 'password', 'admin', 'qwerty']
    if any(pattern in password.lower() for pattern in weak_patterns):
        return False, "Password contains common weak patterns"
    
    return True, "Password is strong"

def check_rate_limit(client_ip: str) -> bool:
    """Check if IP is rate limited due to failed attempts"""
    if client_ip not in failed_login_attempts:
        return True
    
    attempt_data = failed_login_attempts[client_ip]
    
    # Clean old attempts
    if 'lockout_until' in attempt_data:
        if datetime.utcnow() > attempt_data['lockout_until']:
            del failed_login_attempts[client_ip]
            return True
        return False
    
    return True

def record_failed_attempt(client_ip: str, username: str = None):
    """Record a failed login attempt"""
    if client_ip not in failed_login_attempts:
        failed_login_attempts[client_ip] = {
            'count': 0,
            'first_attempt': datetime.utcnow(),
            'usernames': set()
        }
    
    attempt_data = failed_login_attempts[client_ip]
    attempt_data['count'] += 1
    attempt_data['last_attempt'] = datetime.utcnow()
    
    if username:
        attempt_data['usernames'].add(username)
    
    # Lock out after max attempts
    if attempt_data['count'] >= MAX_FAILED_ATTEMPTS:
        attempt_data['lockout_until'] = datetime.utcnow() + LOCKOUT_DURATION
        logger.warning(f"SECURITY: IP {client_ip} locked out after {attempt_data['count']} failed attempts. Usernames: {list(attempt_data['usernames'])}")

def clear_failed_attempts(client_ip: str):
    """Clear failed attempts for successful login"""
    if client_ip in failed_login_attempts:
        del failed_login_attempts[client_ip]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash with timing attack protection"""
    try:
        # Use constant-time comparison to prevent timing attacks
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password with strong salt"""
    # Use higher cost factor for better security (12 rounds)
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with additional security claims"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add security claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "jti": secrets.token_hex(16),  # JWT ID for revocation
        "iss": "url-shortener"  # Issuer
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token with additional security checks"""
    try:
        # Decode with validation
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        issued_at = payload.get("iat")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is too old (additional security)
        if issued_at:
            max_age = timedelta(hours=24)  # Max token age
            if datetime.utcnow() > datetime.fromtimestamp(issued_at) + max_age:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials", 
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_secure_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key_hash(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash"""
    return hash_api_key(api_key) == hashed_key