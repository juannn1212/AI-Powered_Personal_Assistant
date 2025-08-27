from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    estimated_time: Optional[int] = Field(None, ge=1, le=480)  # en minutos

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    category: Optional[str] = Field(None, max_length=100)
    due_date: Optional[datetime] = None
    estimated_time: Optional[int] = Field(None, ge=1, le=480)

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    category: Optional[str]
    due_date: Optional[datetime]
    estimated_time: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
