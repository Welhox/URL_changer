#!/usr/bin/env python3
"""
Database migration script for URL Changer
Creates tables in the target database
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, Base

def migrate_database():
    """Create all tables in the database"""
    print("Starting database migration...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database migration completed successfully!")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Load environment variables (defaults to .env file)
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL', 'Not set')
    print(f"Using DATABASE_URL: {database_url[:50]}...")
    
    if database_url.startswith('sqlite'):
        print("❌ SQLite detected. Please update your .env file to use PostgreSQL.")
        sys.exit(1)
    
    # Run migration
    migrate_database()