from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time, timedelta
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


def _streak(days: set, today: date) -> int:
    """Días consecutivos con registro, contando hacia atrás desde hoy.

    Si hoy todavía no se ha completado, la racha sigue viva desde ayer.
    """
    if not days:
        return 0
    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _to_response(habit: Habit) -> HabitResponse:
    """Convierte un hábito en su respuesta, con racha y última vez completado."""
    today = datetime.utcnow().date()
    completed = [log.completed_at for log in habit.habit_logs if log.completed_at]
    days = {c.date() for c in completed}
    return HabitResponse.model_validate(habit).model_copy(update={
        "last_completed": max(completed) if completed else None,
        "streak": _streak(days, today),
        "completed_today": today in days,
    })

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

        return _to_response(db_habit)
        
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
        return [_to_response(habit) for habit in habits]
        
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

@router.post("/{habit_id}/toggle", response_model=HabitResponse)
async def toggle_habit_today(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca o desmarca el hábito como completado hoy"""
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

        start_of_day = datetime.combine(datetime.utcnow().date(), time.min)
        todays_logs = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.completed_at >= start_of_day
        ).all()

        if todays_logs:
            for log in todays_logs:
                db.delete(log)
        else:
            db.add(HabitLog(habit_id=habit_id, completed_at=datetime.utcnow()))

        db.commit()
        db.refresh(habit)
        return _to_response(habit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling habit: {str(e)}")
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
        habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
        items = [_to_response(h) for h in habits]
        streaks = [h.streak for h in items]

        total = len(items)
        active = sum(1 for h in items if h.is_active)
        completed_today = sum(1 for h in items if h.completed_today)

        return {
            "total": total,
            "active": active,
            "completed_today": completed_today,
            "streak_average": round(sum(streaks) / total, 1) if total else 0,
            "max_streak": max(streaks, default=0),
            # Alias por compatibilidad con pantallas que usan los nombres largos
            "total_habits": total,
            "active_habits": active,
        }
        
    except Exception as e:
        logger.error(f"Error getting habit stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
