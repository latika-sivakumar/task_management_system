from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class ActivityLog(BaseModel):
    task_id: str
    user_id: str
    action: str   # e.g. "created", "updated", "deleted", "category_added", "tag_added"
    timestamp: datetime
    details: Optional[Dict] = None  # to store extra info like old/new values
