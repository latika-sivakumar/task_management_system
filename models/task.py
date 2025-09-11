from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    incomplete = "Incomplete"
    completed = "Completed"

class TaskPriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class TaskCreate(BaseModel):
    title: Optional[str] = ""   # default empty string
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.incomplete
    category_id: Optional[str] = None
    tags: List[str] = []

class TaskResponse(TaskCreate):
    task_id: str
    user_id: str
