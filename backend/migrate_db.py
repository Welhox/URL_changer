#!/usr/bin/env python3
"""
Database migration script for adding user authentication to URL Changer
This script will:
1. Create the users table
2. Add user_id column to url_mappings table
3. Create a default user for existing URLs
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import bcrypt

# Add current directory to path to import modules
sys.path.append(os.path.dirname(__file__))

def migrate_database():
    load_dotenv()
    

    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return False
    
    print(f"Connecting to database: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                print("Creating users table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                print("Adding user_id column to url_mappings table...")
                # Check if user_id column already exists
                result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'url_mappings' AND column_name = 'user_id'
                """))
                
                if not result.fetchone():
                    # Add user_id column (nullable for now)
                    conn.execute(text("""
                        ALTER TABLE url_mappings 
                        ADD COLUMN user_id INTEGER
                    """))
                    print("Added user_id column to url_mappings")
                else:
                    print("user_id column already exists")
                
                # Create a default user for existing URLs
                print("Creating default user...")
                # Use a shorter password to avoid bcrypt issues
                default_password = "default123"
                # Hash password with bcrypt directly
                salt = bcrypt.gensalt()
                default_password_hash = bcrypt.hashpw(default_password.encode('utf-8'), salt).decode('utf-8')
                
                # Check if default user already exists
                result = conn.execute(text("""
                    SELECT id FROM users WHERE username = 'default_user'
                """))
                
                existing_user = result.fetchone()
                
                if not existing_user:
                    result = conn.execute(text("""
                        INSERT INTO users (username, email, hashed_password)
                        VALUES ('default_user', 'default@urlchanger.local', :password_hash)
                        RETURNING id
                    """), {"password_hash": default_password_hash})
                    
                    default_user_id = result.fetchone()[0]
                    print(f"Created default user with ID: {default_user_id}")
                else:
                    default_user_id = existing_user[0]
                    print(f"Using existing default user with ID: {default_user_id}")
                
                # Update existing URLs to belong to default user
                print("Assigning existing URLs to default user...")
                result = conn.execute(text("""
                    UPDATE url_mappings 
                    SET user_id = :user_id 
                    WHERE user_id IS NULL
                """), {"user_id": default_user_id})
                
                updated_rows = result.rowcount
                print(f"Updated {updated_rows} existing URLs")
                
                # Make user_id NOT NULL after updating existing records
                print("Making user_id column NOT NULL...")
                conn.execute(text("""
                    ALTER TABLE url_mappings 
                    ALTER COLUMN user_id SET NOT NULL
                """))
                
                # Add foreign key constraint
                print("Adding foreign key constraint...")
                conn.execute(text("""
                    ALTER TABLE url_mappings 
                    ADD CONSTRAINT fk_url_mappings_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                """))
                
                # Commit the transaction
                trans.commit()
                print("✅ Database migration completed successfully!")
                
                print(f"""
📋 Migration Summary:
- Created users table
- Added user_id column to url_mappings table
- Created default user (username: 'default_user', password: 'default123')
- Assigned {updated_rows} existing URLs to default user
- Added foreign key constraint

🔑 You can login with:
   Username: default_user
   Password: default123
                """)
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)