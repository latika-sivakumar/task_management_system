# routes/user.py
from fastapi import APIRouter, Depends
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
