# routes/task.py
from fastapi import APIRouter, Depends, HTTPException, Query
from models.task import TaskCreate, TaskResponse, TaskStatus,TaskPriority
from database import db
from dependencies import get_current_user
from uuid import uuid4
from typing import Optional
from datetime import datetime, timedelta
from models.activity import ActivityLog

router = APIRouter(prefix="/tasks", tags=["Tasks"])
tasks_collection = db["tasks"]
categories_collection = db["categories"]
tags_collection = db["tags"]
activity_collection = db["activity_logs"]

# Create Task
@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_doc = task.dict()
    task_doc["task_id"] = str(uuid4())
    task_doc["user_id"] = current_user["id"]

    # Set defaults if missing
    task_doc.setdefault("title", "")
    task_doc.setdefault("description", "")
    task_doc.setdefault("status", TaskStatus.incomplete.value)
    task_doc.setdefault("priority", TaskPriority.medium.value)
    task_doc.setdefault("due_date", datetime.utcnow())

    await tasks_collection.insert_one(task_doc)
    await log_activity(task_doc["task_id"], current_user["id"], "created", {"title": task_doc["title"]})

    # Remove MongoDB _id
    task_doc.pop("_id", None)

    return TaskResponse(**task_doc)

# Get all tasks for user
@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    skip: int = Query(0, description="Number of tasks to skip"),
    limit: int = Query(10, description="Maximum number of tasks to return"),
    current_user: dict = Depends(get_current_user)
):
    query = {"user_id": current_user["id"]}

    if status:
        query["status"] = status.value
    if priority:
        query["priority"] = priority.value
    if category_id:
        query["category_id"] = category_id
    if tag_id:
        query["tags"] = tag_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]

    tasks = []
    cursor = tasks_collection.find(query).skip(skip).limit(limit)
    async for task in cursor:
        task.pop("_id", None)
        tasks.append(TaskResponse(**task))
    return tasks

# Update Task
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, current_user: dict = Depends(get_current_user)):
    existing_task = await tasks_collection.find_one({"task_id": task_id, "user_id": current_user["id"]})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_task = task.dict()
    updated_task["task_id"] = task_id
    updated_task["user_id"] = current_user["id"]

    await tasks_collection.replace_one({"task_id": task_id}, updated_task)
    await log_activity(task_id, current_user["id"], "updated", {"updated_fields": updated_task})

    # Remove _id before returning
    updated_task.pop("_id", None)
    return TaskResponse(**updated_task)

# Delete Task
@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await tasks_collection.delete_one({"task_id": task_id, "user_id": current_user["id"]})
    await log_activity(task_id, current_user["id"], "deleted")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}

# Assign category to task (create if doesn't exist)
@router.post("/{task_id}/add-category")
async def add_category(task_id: str, category_name: str):
    task = await tasks_collection.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if category already exists
    category = await categories_collection.find_one({"name": category_name})
    if not category:
        # Create new category
        new_category = {"id": str(uuid4()), "name": category_name}
        await categories_collection.insert_one(new_category)
        category_id = new_category["id"]
    else:
        category_id = category["id"]

    # Assign category to task
    await tasks_collection.update_one({"task_id": task_id}, {"$set": {"category_id": category_id}})
    await log_activity(task_id, task["user_id"], "category_added", {"category": category_name})

    return {"task_id": task_id, "category_id": category_id, "category_name": category_name}

# Assign tag to task (create if doesn't exist)
@router.post("/{task_id}/add-tag")
async def add_tag(task_id: str, tag_name: str):
    task = await tasks_collection.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if tag already exists
    tag = await tags_collection.find_one({"name": tag_name})
    if not tag:
        # Create new tag
        new_tag = {"id": str(uuid4()), "name": tag_name}
        await tags_collection.insert_one(new_tag)
        tag_id = new_tag["id"]
    else:
        tag_id = tag["id"]

    # Assign tag to task
    task_tags = task.get("tags", [])
    if tag_id not in task_tags:
        task_tags.append(tag_id)
        await tasks_collection.update_one({"task_id": task_id}, {"$set": {"tags": task_tags}})
        await log_activity(task_id, task["user_id"], "tag_added", {"tag": tag_name})

    return {"task_id": task_id, "tags": task_tags}

async def log_activity(task_id: str, user_id: str, action: str, details: dict = None):
    log_doc = ActivityLog(
        task_id=task_id,
        user_id=user_id,
        action=action,
        timestamp=datetime.utcnow(),
        details=details
    ).dict()
    await activity_collection.insert_one(log_doc)

@router.get("/{task_id}/logs")
async def get_task_logs(task_id: str, current_user: dict = Depends(get_current_user)):
    logs = await activity_collection.find({"task_id": task_id, "user_id": current_user["id"]}).to_list(100)
    for log in logs:
        log.pop("_id", None)
    return logs
