"""
Security improvements for URL Shortener
"""
import re
from urllib.parse import urlparse
from typing import List

# URL Security Validation
BLOCKED_DOMAINS = [
    'bit.ly', 'tinyurl.com', 't.co',  # Prevent redirect chains
    'localhost', '127.0.0.1'          # Block local redirects
]

BLOCKED_SCHEMES = ['javascript', 'data', 'file', 'ftp']

def validate_redirect_url(url: str) -> bool:
    """Validate URL before redirect to prevent open redirect attacks"""
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme.lower() in BLOCKED_SCHEMES:
            return False
        
        # Must be HTTP/HTTPS
        if parsed.scheme.lower() not in ['http', 'https']:
            return False
        
        # Check for blocked domains
        hostname = parsed.hostname
        if hostname:
            hostname = hostname.lower()
            for blocked in BLOCKED_DOMAINS:
                if blocked in hostname:
                    return False
        
        # Block IP addresses in production
        import os
        if os.getenv("ENVIRONMENT") == "production":
            # Block private IP ranges
            ip_patterns = [
                r'^127\.',           # Loopback
                r'^10\.',            # Private Class A
                r'^192\.168\.',      # Private Class C
                r'^172\.(1[6-9]|2[0-9]|3[01])\.',  # Private Class B
                r'^0\.',             # This network
                r'^169\.254\.',      # Link-local
            ]
            
            for pattern in ip_patterns:
                if re.match(pattern, hostname or ''):
                    return False
        
        return True
        
    except Exception:
        return False

def sanitize_custom_code(code: str) -> str:
    """Sanitize custom code to prevent injection"""
    # Remove any non-alphanumeric, hyphen, underscore characters
    return re.sub(r'[^a-zA-Z0-9_-]', '', code)

def validate_user_agent(user_agent: str) -> bool:
    """Basic bot detection"""
    if not user_agent:
        return False
        
    bot_patterns = [
        r'bot', r'crawler', r'spider', r'scraper',
        r'curl', r'wget', r'python', r'java'
    ]
    
    user_agent_lower = user_agent.lower()
    for pattern in bot_patterns:
        if re.search(pattern, user_agent_lower):
            return False
    
    return True