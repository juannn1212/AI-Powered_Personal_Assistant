from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str

class CreateTaskRequest(BaseModel):
    description: str
    priority: str = "medium"
    due_date: Optional[str] = None

class CreateHabitRequest(BaseModel):
    description: str
    frequency: str = "daily"

class ChatResponse(BaseModel):
    success: bool
    data: dict

