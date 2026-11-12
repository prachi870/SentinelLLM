"""
routers/init.py — Initialization endpoints

Endpoints:
- POST /init/demo-user — Create demo user (one-time setup)
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth_utils import hash_password
from database import get_db
from models import User

router = APIRouter(prefix="/init", tags=["initialization"])


@router.post("/demo-user")
def create_demo_user(db: Session = Depends(get_db)):
    """
    Create the demo user for testing.
    
    This endpoint is idempotent - safe to call multiple times.
    """
    # Check if demo user already exists
    existing = db.query(User).filter(User.email == "test@sentinelloop.ai").first()
    
    if existing:
        return {
            "status": "exists",
            "message": "Demo user already exists",
            "email": "test@sentinelloop.ai"
        }
    
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
    
    return {
        "status": "created",
        "message": "Demo user created successfully",
        "email": "test@sentinelloop.ai",
        "user_id": str(demo_user.id)
    }
