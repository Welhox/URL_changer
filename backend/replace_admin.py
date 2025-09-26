#!/usr/bin/env python3
"""
Script to replace the default admin with a new admin user
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from database import SessionLocal
from auth import get_password_hash

def replace_admin():
    """Replace default admin with new admin credentials"""
    db = SessionLocal()
    try:
        print("=== Replacing Admin User ===")
        
        # Delete the existing default admin
        print("Removing default admin user...")
        result = db.execute(text("DELETE FROM users WHERE username = 'admin'"))
        if result.rowcount > 0:
            print("✓ Default admin user removed")
        else:
            print("ℹ Default admin user not found (may have been removed already)")
        
        # Check if new admin already exists
        result = db.execute(text("SELECT COUNT(*) as count FROM users WHERE username = :username"), 
                          {'username': 'casi'})
        
        if result.fetchone()[0] > 0:
            print("✗ User 'casi' already exists!")
            return False
        
        # Create new admin
        print("Creating new admin user...")
        hashed_password = get_password_hash("casi42")
        
        db.execute(text("""
            INSERT INTO users (username, email, hashed_password, is_active, is_admin, created_at)
            VALUES (:username, :email, :password, TRUE, TRUE, NOW())
        """), {
            'username': 'casi',
            'email': 'casi.lehtovuori@gmail.com',
            'password': hashed_password
        })
        
        db.commit()
        print("✓ New admin user created successfully!")
        print("  Username: casi")
        print("  Password: casi42")
        print("  Email: casi.lehtovuori@gmail.com")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = replace_admin()
    if success:
        print("\n=== Admin Replacement Complete ===")
        print("You can now log in with the new admin credentials!")
    else:
        print("\n=== Admin Replacement Failed ===")
        sys.exit(1)