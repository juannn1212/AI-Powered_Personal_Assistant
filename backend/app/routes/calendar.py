from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.database import get_db, User
from app.routes.auth import get_current_active_user

router = APIRouter()

# Pydantic models
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_all_day: bool = False
    reminder_minutes: Optional[int] = 15

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_all_day: Optional[bool] = None
    reminder_minutes: Optional[int] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    is_all_day: bool
    reminder_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime

@router.post("/events", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new calendar event
    """
    try:
        # Validate time range
        if event_data.start_time >= event_data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
        
        # Create event (placeholder - would need Event model in database)
        event = {
            "id": 1,  # Placeholder
            "title": event_data.title,
            "description": event_data.description,
            "start_time": event_data.start_time,
            "end_time": event_data.end_time,
            "location": event_data.location,
            "is_all_day": event_data.is_all_day,
            "reminder_minutes": event_data.reminder_minutes,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return EventResponse(**event)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating event: {str(e)}"
        )

@router.get("/events", response_model=List[EventResponse])
async def get_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get calendar events for a date range
    """
    try:
        # Placeholder events - would query database
        events = [
            {
                "id": 1,
                "title": "Reunión de trabajo",
                "description": "Reunión semanal del equipo",
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "location": "Oficina",
                "is_all_day": False,
                "reminder_minutes": 15,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        
        return [EventResponse(**event) for event in events]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving events: {str(e)}"
        )

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific calendar event
    """
    try:
        # Placeholder - would query database
        event = {
            "id": event_id,
            "title": "Evento de ejemplo",
            "description": "Descripción del evento",
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "location": "Ubicación",
            "is_all_day": False,
            "reminder_minutes": 15,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return EventResponse(**event)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving event: {str(e)}"
        )

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a calendar event
    """
    try:
        # Placeholder - would update database
        event = {
            "id": event_id,
            "title": event_data.title or "Evento actualizado",
            "description": event_data.description,
            "start_time": event_data.start_time or datetime.now(),
            "end_time": event_data.end_time or datetime.now(),
            "location": event_data.location,
            "is_all_day": event_data.is_all_day or False,
            "reminder_minutes": event_data.reminder_minutes,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return EventResponse(**event)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating event: {str(e)}"
        )

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a calendar event
    """
    try:
        # Placeholder - would delete from database
        return {"message": f"Event {event_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting event: {str(e)}"
        )

@router.get("/schedule/conflicts")
async def check_schedule_conflicts(
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check for schedule conflicts
    """
    try:
        # Placeholder - would check database for conflicts
        conflicts = []
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking conflicts: {str(e)}"
        )

@router.get("/schedule/suggestions")
async def get_schedule_suggestions(
    duration_minutes: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get schedule suggestions based on availability
    """
    try:
        # Placeholder - would analyze calendar and suggest times
        suggestions = [
            {
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "confidence": 0.8
            }
        ]
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting suggestions: {str(e)}"
        )
