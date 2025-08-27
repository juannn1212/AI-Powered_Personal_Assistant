from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.models.habit import Habit, HabitLog
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitLogCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo hábito"""
    try:
        db_habit = Habit(
            user_id=current_user.id,
            name=habit_data.name,
            description=habit_data.description,
            frequency=habit_data.frequency,
            time_of_day=habit_data.time_of_day,
            category=habit_data.category,
            motivation_tip=habit_data.motivation_tip
        )
        
        db.add(db_habit)
        db.commit()
        db.refresh(db_habit)
        
        return HabitResponse.model_validate(db_habit)
        
    except Exception as e:
        logger.error(f"Error creating habit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[HabitResponse])
async def get_habits(
    category: Optional[str] = None,
    frequency: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener hábitos del usuario"""
    try:
        query = db.query(Habit).filter(Habit.user_id == current_user.id)
        
        if category:
            query = query.filter(Habit.category == category)
        if frequency:
            query = query.filter(Habit.frequency == frequency)
        
        habits = query.order_by(Habit.created_at.desc()).all()
        return [HabitResponse.model_validate(habit) for habit in habits]
        
    except Exception as e:
        logger.error(f"Error getting habits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un hábito específico"""
    try:
        habit = db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        ).first()
        
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado"
            )
        
        return HabitResponse.model_validate(habit)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting habit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un hábito"""
    try:
        habit = db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        ).first()
        
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado"
            )
        
        # Actualizar campos
        for field, value in habit_data.dict(exclude_unset=True).items():
            setattr(habit, field, value)
        
        habit.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(habit)
        
        return HabitResponse.model_validate(habit)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating habit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un hábito"""
    try:
        habit = db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        ).first()
        
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado"
            )
        
        db.delete(habit)
        db.commit()
        
        return {"message": "Hábito eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting habit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/{habit_id}/log")
async def log_habit_completion(
    habit_id: int,
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar la completación de un hábito"""
    try:
        habit = db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        ).first()
        
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado"
            )
        
        habit_log = HabitLog(
            habit_id=habit_id,
            completed_at=log_data.completed_at or datetime.utcnow(),
            notes=log_data.notes
        )
        
        db.add(habit_log)
        db.commit()
        
        return {"message": "Hábito registrado como completado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging habit completion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{habit_id}/logs")
async def get_habit_logs(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener logs de un hábito específico"""
    try:
        habit = db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == current_user.id
        ).first()
        
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hábito no encontrado"
            )
        
        logs = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id
        ).order_by(HabitLog.completed_at.desc()).all()
        
        return [
            {
                "id": log.id,
                "completed_at": log.completed_at,
                "notes": log.notes
            }
            for log in logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting habit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/stats/summary")
async def get_habit_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de hábitos"""
    try:
        total_habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
        active_habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True
        ).count()
        
        # Calcular hábitos completados hoy
        today = date.today()
        today_logs = db.query(HabitLog).join(Habit).filter(
            Habit.user_id == current_user.id,
            HabitLog.completed_at >= today
        ).count()
        
        # Calcular racha más larga
        all_logs = db.query(HabitLog).join(Habit).filter(
            Habit.user_id == current_user.id
        ).order_by(HabitLog.completed_at).all()
        
        max_streak = 0
        current_streak = 0
        last_date = None
        
        for log in all_logs:
            log_date = log.completed_at.date()
            if last_date is None or (log_date - last_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            
            max_streak = max(max_streak, current_streak)
            last_date = log_date
        
        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "completed_today": today_logs,
            "max_streak": max_streak,
            "current_streak": current_streak
        }
        
    except Exception as e:
        logger.error(f"Error getting habit stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
