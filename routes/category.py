from fastapi import APIRouter, Depends, HTTPException
from models.category import CategoryCreate, CategoryResponse
from database import db
from dependencies import get_current_user
from uuid import uuid4

router = APIRouter(prefix="/categories", tags=["Categories"])
categories_collection = db["categories"]

# Create Category
@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user)):
    category_doc = {
        "id": str(uuid4()),
        "name": category.name
    }
    await categories_collection.insert_one(category_doc)
    return CategoryResponse(**category_doc)

# List all categories
@router.get("/", response_model=list[CategoryResponse])
async def list_categories():
    categories = await categories_collection.find().to_list(100)
    return [CategoryResponse(**cat) for cat in categories]