from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import UserCreate, UserResponse
from database import db
from passlib.context import CryptContext
from utils.jwt_handler import verify_password, get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

# Use the same collection
users_collection = db["users"]

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = get_password_hash(user.password)

    # Create new user doc
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw
    }

    result = await users_collection.insert_one(user_doc)

    return UserResponse(
        id=str(result.inserted_id),
        username=user.username,
        email=user.email
    )

from fastapi import Form

@router.post("/login")
async def login_user(
    username: str = Form(..., title="Email", description="Enter your email here"),
    password: str = Form(..., title="Password", description="Enter your password")
):
    user = await users_collection.find_one({"email": username})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
