"""
create_demo_user.py - Create the demo user for testing

Run this script once after deploying to create the test@sentinelloop.ai user.

Usage:
    python create_demo_user.py
"""

from datetime import datetime
from database import SessionLocal
from models import User
from auth_utils import hash_password

def create_demo_user():
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing = db.query(User).filter(User.email == "test@sentinelloop.ai").first()
        
        if existing:
            print("✅ Demo user already exists!")
            return
        
        # Create demo user
        demo_user = User(
            email="test@sentinelloop.ai",
            full_name="Demo User",
            password_hash=hash_password("testpass123"),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        print("✅ Demo user created successfully!")
        print(f"   Email: test@sentinelloop.ai")
        print(f"   Password: testpass123")
        print(f"   User ID: {demo_user.id}")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()
