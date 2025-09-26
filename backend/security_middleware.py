"""
Security middleware and headers for FastAPI application
"""
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import time
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Only add HSTS in production with HTTPS
        import os
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP - Allow same origin and specific domains
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class RateLimitByUserMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting per user/IP"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.user_requests = {}  # In production, use Redis
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = None
        
        # Try to get user from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                user_id = payload.get("user_id")
            except:
                pass
        
        identifier = f"user_{user_id}" if user_id else f"ip_{client_ip}"
        
        # Rate limiting logic
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        if identifier not in self.user_requests:
            self.user_requests[identifier] = {}
        
        user_minute_data = self.user_requests[identifier]
        
        # Clean old windows (keep only current minute)
        old_windows = [w for w in user_minute_data if w < minute_window - 1]
        for w in old_windows:
            del user_minute_data[w]
        
        # Count requests in current window
        current_requests = user_minute_data.get(minute_window, 0)
        
        # Check if over limit
        if current_requests >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return StarletteResponse(
                content="Rate limit exceeded", 
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Increment counter
        user_minute_data[minute_window] = current_requests + 1
        
        response = await call_next(request)
        return response

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log security-relevant events"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log sensitive operations
        sensitive_paths = ['/api/register', '/api/login', '/api/shorten', '/api/slack/events']
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        if any(request.url.path.startswith(path) for path in sensitive_paths):
            logger.info(f"AUDIT: {request.method} {request.url.path} from {client_ip} UA: {user_agent[:100]}")
        
        response = await call_next(request)
        
        # Log failed authentication attempts
        if request.url.path.startswith('/api/login') and response.status_code == 401:
            logger.warning(f"SECURITY: Failed login attempt from {client_ip}")
        
        # Log suspicious activity
        if response.status_code == 404 and 'admin' in request.url.path.lower():
            logger.warning(f"SECURITY: Admin path probe from {client_ip}: {request.url.path}")
        
        return response