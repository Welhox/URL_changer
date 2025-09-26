#!/usr/bin/env python3
"""
Migration script to add is_admin column to users table
Run this after updating the database.py schema
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from database import engine, SessionLocal
from auth import get_password_hash

def migrate_add_admin_column():
    """Add is_admin column to existing users table"""
    with engine.connect() as connection:
        # Check if column already exists (PostgreSQL)
        result = connection.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_admin'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding is_admin column to users table...")
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            connection.commit()
            print("✓ is_admin column added successfully")
        else:
            print("✓ is_admin column already exists")

def create_default_admin():
    """Create a default admin user if no admin exists"""
    db = SessionLocal()
    try:
        # Check if any admin exists
        result = db.execute(text("SELECT COUNT(*) as count FROM users WHERE is_admin = TRUE")).fetchone()
        
        if result[0] == 0:
            print("Creating default admin user...")
            
            # Create default admin
            hashed_password = get_password_hash("admin123")
            
            db.execute(text("""
                INSERT INTO users (username, email, hashed_password, is_active, is_admin, created_at)
                VALUES (:username, :email, :password, TRUE, TRUE, NOW())
            """), {
                'username': 'admin',
                'email': 'admin@organization.com',
                'password': hashed_password
            })
            
            db.commit()
            print("✓ Default admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Email: admin@organization.com")
        else:
            print("✓ Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def update_existing_user_as_admin(username: str):
    """Make an existing user an admin"""
    db = SessionLocal()
    try:
        result = db.execute(text("""
            UPDATE users SET is_admin = TRUE WHERE username = :username
        """), {'username': username})
        
        if result.rowcount > 0:
            db.commit()
            print(f"✓ User '{username}' is now an admin")
        else:
            print(f"✗ User '{username}' not found")
            
    except Exception as e:
        print(f"Error updating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== URL Changer Admin Migration ===")
    
    # Add admin column
    migrate_add_admin_column()
    
    # Create default admin if needed
    create_default_admin()
    
    # Option to make existing user admin
    if len(sys.argv) > 1:
        existing_username = sys.argv[1]
        print(f"\nMaking existing user '{existing_username}' an admin...")
        update_existing_user_as_admin(existing_username)
    
    print("\n=== Migration Complete ===")
    print("You can now:")
    print("1. Log in as 'admin' with password 'admin123'")
    print("2. Or run: python migrate_admin.py <username> to make existing user admin")