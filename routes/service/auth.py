from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from fastapi import HTTPException, Depends, Request
from passlib.context import CryptContext
from schemas import UserBase
from dotenv import load_dotenv

load_dotenv()



ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY")
REFRESH_TOKEN_EXPIRE_MINUTES = float(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme


# Hash password
async def hash_password(password: str):
    return pwd_context.hash(password)


# Verify password
async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Generate JWT token
async def create_access_token(data: UserBase, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub":str(data.id)}
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
   
    return encoded_jwt

# Generate Refresh JWT token
async def create_refresh_token(data: UserBase, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub":str(data.id)}
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
   
    return encoded_jwt


# Verify JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError :
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_refresh_token(token:str):
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError :
        raise HTTPException(status_code=401, detail="Invalid token")
# Get user from token
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_token(token)
