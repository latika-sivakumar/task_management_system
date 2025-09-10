from pydantic import BaseModel
from datetime import datetime

class ReminderCreate(BaseModel):
    task_id: str
    remind_at: datetime  # when user wants to be reminded

class ReminderResponse(BaseModel):
    id: str
    task_id: str
    remind_at: datetime
