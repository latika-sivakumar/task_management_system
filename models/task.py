from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import uuid4

class TaskStatus(str, Enum):
    incomplete = "Incomplete"
    completed = "Completed"

class TaskPriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.incomplete
    category_id: Optional[str] = None  # NEW
    tags: Optional[List[str]] = []  # NEW, list of tag IDs

class TaskResponse(TaskCreate):
    task_id: str
    user_id: str
