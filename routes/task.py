# routes/task.py
from fastapi import APIRouter, Depends, HTTPException
from models.task import TaskCreate, TaskResponse, TaskStatus,TaskPriority
from database import db
from dependencies import get_current_user
from uuid import uuid4
from datetime import datetime, timedelta

router = APIRouter(prefix="/tasks", tags=["Tasks"])
tasks_collection = db["tasks"]

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

    return TaskResponse(**task_doc)

# Get all tasks for user
@router.get("/", response_model=list[TaskResponse])
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = []
    cursor = tasks_collection.find({"user_id": current_user["id"]})
    async for task in cursor:
        task.pop("_id", None)  # REMOVE _id
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

    # Remove _id before returning
    updated_task.pop("_id", None)
    return TaskResponse(**updated_task)

# Delete Task
@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await tasks_collection.delete_one({"task_id": task_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}

# Assign category to task
@router.post("/{task_id}/add-category")
async def add_category(task_id: str, category_id: str):
    task = await tasks_collection.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task["category_id"] = category_id
    await tasks_collection.update_one({"task_id": task_id}, {"$set": {"category_id": category_id}})
    return {"task_id": task_id, "category_id": category_id}

# Assign tag to task
@router.post("/{task_id}/add-tag")
async def add_tag(task_id: str, tag_id: str):
    task = await tasks_collection.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_tags = task.get("tags", [])
    if tag_id not in task_tags:
        task_tags.append(tag_id)
        await tasks_collection.update_one({"task_id": task_id}, {"$set": {"tags": task_tags}})
    return {"task_id": task_id, "tags": task_tags}