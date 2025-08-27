from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    frequency: str = Field(default="daily", pattern="^(daily|weekly|monthly)$")
    time_of_day: str = Field(default="flexible", pattern="^(morning|afternoon|evening|flexible)$")
    category: Optional[str] = Field(None, max_length=100)
    motivation_tip: Optional[str] = Field(None, max_length=500)

class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    time_of_day: Optional[str] = Field(None, pattern="^(morning|afternoon|evening|flexible)$")
    category: Optional[str] = Field(None, max_length=100)
    motivation_tip: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    frequency: str
    time_of_day: str
    category: Optional[str]
    motivation_tip: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HabitLogCreate(BaseModel):
    completed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
