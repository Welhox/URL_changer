#!/usr/bin/env python3
"""
Migration script to convert existing usernames and emails to lowercase
for case-insensitive authentication compatibility.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from database import SessionLocal, User

def migrate_usernames_to_lowercase():
    """Convert all existing usernames and emails to lowercase"""
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        print(f"Found {len(users)} users in database")
        
        updated_count = 0
        
        for user in users:
            original_username = user.username
            original_email = user.email
            
            # Convert to lowercase
            new_username = user.username.lower()
            new_email = user.email.lower()
            
            # Check if any changes are needed
            if user.username != new_username or user.email != new_email:
                print(f"Updating user: {original_username} -> {new_username}")
                print(f"  Email: {original_email} -> {new_email}")
                
                user.username = new_username
                user.email = new_email
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Successfully updated {updated_count} users to lowercase")
        else:
            print("\n✅ All usernames and emails are already lowercase - no changes needed")
            
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during migration: {e}")
        return False
        
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("🔄 Starting username/email lowercase migration...")
    success = migrate_usernames_to_lowercase()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNow users can login with any case variation of their username:")
        print("  - 'Casi', 'casi', 'CASI' will all work for the same user")
        print("  - New usernames will be automatically stored in lowercase")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)