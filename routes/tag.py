from fastapi import APIRouter, Depends, HTTPException
from models.tag import TagCreate, TagResponse
from database import db
from dependencies import get_current_user
from uuid import uuid4

router = APIRouter(prefix="/tags", tags=["Tags"])
tags_collection = db["tags"]

# Create Tag
@router.post("/", response_model=TagResponse)
async def create_tag(tag: TagCreate, current_user: dict = Depends(get_current_user)):
    tag_doc = {
        "id": str(uuid4()),
        "name": tag.name
    }
    await tags_collection.insert_one(tag_doc)
    return TagResponse(**tag_doc)

# List all tags
@router.get("/", response_model=list[TagResponse])
async def list_tags():
    tags = await tags_collection.find().to_list(100)
    return [TagResponse(**tag) for tag in tags]
