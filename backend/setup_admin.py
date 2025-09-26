#!/usr/bin/env python3
"""
Script to check existing users and manage admin replacement
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import text
from database import SessionLocal
from auth import get_password_hash

def list_users():
    """List all users in the database"""
    db = SessionLocal()
    try:
        print("=== Current Users in Database ===")
        result = db.execute(text("""
            SELECT username, email, is_admin, is_active, created_at 
            FROM users 
            ORDER BY created_at
        """))
        
        users = result.fetchall()
        if not users:
            print("No users found in database")
        else:
            for user in users:
                admin_status = "ADMIN" if user[2] else "USER"
                active_status = "ACTIVE" if user[3] else "INACTIVE"
                print(f"  • {user[0]} ({user[1]}) - {admin_status}, {active_status}")
        
        return users
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        db.close()

def update_existing_user():
    """Update existing 'casi' user to be admin with new credentials"""
    db = SessionLocal()
    try:
        print("\n=== Updating Existing User 'casi' ===")
        
        # Update the existing user
        hashed_password = get_password_hash("casi42")
        
        result = db.execute(text("""
            UPDATE users 
            SET email = :email, 
                hashed_password = :password, 
                is_admin = TRUE, 
                is_active = TRUE
            WHERE username = :username
        """), {
            'username': 'casi',
            'email': 'casi.lehtovuori@gmail.com',
            'password': hashed_password
        })
        
        if result.rowcount > 0:
            db.commit()
            print("✓ User 'casi' updated successfully!")
            print("  Username: casi")
            print("  Password: casi42")
            print("  Email: casi.lehtovuori@gmail.com")
            print("  Status: ADMIN, ACTIVE")
            return True
        else:
            print("✗ User 'casi' not found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def remove_other_admins():
    """Remove other admin users except 'casi'"""
    db = SessionLocal()
    try:
        print("\n=== Removing Other Admin Users ===")
        
        result = db.execute(text("""
            UPDATE users 
            SET is_admin = FALSE 
            WHERE username != 'casi' AND is_admin = TRUE
        """))
        
        if result.rowcount > 0:
            db.commit()
            print(f"✓ Removed admin privileges from {result.rowcount} other users")
        else:
            print("ℹ No other admin users found")
            
        # Also remove the default admin if it still exists
        result = db.execute(text("DELETE FROM users WHERE username = 'admin'"))
        if result.rowcount > 0:
            db.commit()
            print("✓ Removed default admin user")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # List current users
    users = list_users()
    
    # Update existing 'casi' user or create new one
    success = update_existing_user()
    
    if success:
        # Remove other admin privileges
        remove_other_admins()
        
        print("\n=== Final User Status ===")
        list_users()
        
        print("\n=== Admin Setup Complete ===")
        print("You can now log in as 'casi' with password 'casi42'")
    else:
        print("\n=== Setup Failed ===")
        sys.exit(1)