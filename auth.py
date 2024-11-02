from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for password management
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Authentication and role management
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Here, implement your JWT token verification and user extraction logic
    return {"username": "user", "role": "author", "id": 1}  # Placeholder for actual user extraction

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    return current_user

def get_user_role(current_user: dict = Depends(get_current_active_user)):
    return current_user.get("role")
