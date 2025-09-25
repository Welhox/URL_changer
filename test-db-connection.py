#!/usr/bin/env python3
"""
Test database connection for URL Changer
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables (defaults to .env file)
load_dotenv()

try:
    # Import database connection
    sys.path.append('backend')
    from database import engine
    
    print("🔍 Testing database connection...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    
    # Test connection
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("✅ Database connection successful!")
        print(f"Test query result: {result.fetchone()}")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Check your DATABASE_URL in .env.production")
    print("2. Verify your Supabase password is correct")
    print("3. Ensure your Supabase project is active")
    sys.exit(1)