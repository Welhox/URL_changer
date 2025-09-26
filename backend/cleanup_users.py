#!/usr/bin/env python3
"""
Script to remove all non-admin users from the database
"""

from sqlalchemy.orm import Session
from database import SessionLocal, User, URLMapping
import os

def cleanup_non_admin_users():
    """Remove all non-admin users and their associated URLs from the database"""
    
    # Create database session
    db = SessionLocal()
    
    try:
        # First, show current users
        print("Current users in database:")
        print("-" * 50)
        users = db.query(User).all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
        
        print(f"\nTotal users: {len(users)}")
        
        # Find non-admin users
        non_admin_users = db.query(User).filter(User.is_admin == False).all()
        
        if not non_admin_users:
            print("\nNo non-admin users found. Nothing to remove.")
            return
        
        print(f"\nFound {len(non_admin_users)} non-admin users to remove:")
        for user in non_admin_users:
            print(f"- {user.username} (ID: {user.id}, Email: {user.email})")
        
        # Remove URLs created by non-admin users
        for user in non_admin_users:
            urls = db.query(URLMapping).filter(URLMapping.user_id == user.id).all()
            if urls:
                print(f"\nRemoving {len(urls)} URLs created by user '{user.username}'")
                for url in urls:
                    db.delete(url)
        
        # Remove non-admin users
        for user in non_admin_users:
            print(f"Removing user: {user.username}")
            db.delete(user)
        
        # Commit changes
        db.commit()
        print("\n✅ Successfully removed all non-admin users and their URLs")
        
        # Show remaining users
        print("\nRemaining users in database:")
        print("-" * 50)
        remaining_users = db.query(User).all()
        for user in remaining_users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
        
        print(f"\nTotal remaining users: {len(remaining_users)}")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Cleaning up non-admin users from database...")
    cleanup_non_admin_users()
    print("\n🎉 Cleanup completed!")