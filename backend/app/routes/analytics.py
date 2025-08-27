from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.models.task import Task
from app.models.habit import Habit, HabitLog
from app.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIService()

@router.get("/productivity")
async def get_productivity_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener analytics de productividad con datos reales"""
    try:
        # Obtener estadísticas de tareas
        total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
        completed_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status == "completed"
        ).count()
        
        # Calcular tasa de completación
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Tareas por prioridad
        priority_stats = db.query(
            Task.priority,
            func.count(Task.id).label('count')
        ).filter(Task.user_id == current_user.id).group_by(Task.priority).all()
        
        # Tareas por categoría
        category_stats = db.query(
            Task.category,
            func.count(Task.id).label('count')
        ).filter(
            Task.user_id == current_user.id,
            Task.category.isnot(None)
        ).group_by(Task.category).all()
        
        # Tareas completadas en los últimos 7 días
        week_ago = date.today() - timedelta(days=7)
        recent_completions = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.completed_at >= week_ago
        ).count()
        
        # Tareas vencidas
        overdue_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.due_date < date.today(),
            Task.status.in_(["pending", "in_progress"])
        ).count()
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completion_rate, 2),
            "recent_completions": recent_completions,
            "overdue_tasks": overdue_tasks,
            "priority_distribution": [
                {"priority": stat.priority, "count": stat.count}
                for stat in priority_stats
            ],
            "category_distribution": [
                {"category": stat.category, "count": stat.count}
                for stat in category_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting productivity analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/habits")
async def get_habits_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener analytics de hábitos con datos reales"""
    try:
        # Estadísticas generales de hábitos
        total_habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
        active_habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True
        ).count()
        
        # Hábitos completados hoy
        today = date.today()
        today_completions = db.query(HabitLog).join(Habit).filter(
            Habit.user_id == current_user.id,
            HabitLog.completed_at >= today
        ).count()
        
        # Hábitos por categoría
        category_stats = db.query(
            Habit.category,
            func.count(Habit.id).label('count')
        ).filter(
            Habit.user_id == current_user.id,
            Habit.category.isnot(None)
        ).group_by(Habit.category).all()
        
        # Hábitos por frecuencia
        frequency_stats = db.query(
            Habit.frequency,
            func.count(Habit.id).label('count')
        ).filter(Habit.user_id == current_user.id).group_by(Habit.frequency).all()
        
        # Racha más larga
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
        
        # Completaciones de la semana
        week_ago = date.today() - timedelta(days=7)
        week_completions = db.query(HabitLog).join(Habit).filter(
            Habit.user_id == current_user.id,
            HabitLog.completed_at >= week_ago
        ).count()
        
        return {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "today_completions": today_completions,
            "week_completions": week_completions,
            "max_streak": max_streak,
            "current_streak": current_streak,
            "category_distribution": [
                {"category": stat.category, "count": stat.count}
                for stat in category_stats
            ],
            "frequency_distribution": [
                {"frequency": stat.frequency, "count": stat.count}
                for stat in frequency_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting habits analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/tasks")
async def get_tasks_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener analytics detallados de tareas"""
    try:
        # Tareas por estado
        status_stats = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(Task.user_id == current_user.id).group_by(Task.status).all()
        
        # Tareas por mes (últimos 6 meses)
        six_months_ago = date.today() - timedelta(days=180)
        monthly_stats = db.query(
            extract('month', Task.created_at).label('month'),
            extract('year', Task.created_at).label('year'),
            func.count(Task.id).label('count')
        ).filter(
            Task.user_id == current_user.id,
            Task.created_at >= six_months_ago
        ).group_by(
            extract('month', Task.created_at),
            extract('year', Task.created_at)
        ).order_by(
            extract('year', Task.created_at),
            extract('month', Task.created_at)
        ).all()
        
        # Tiempo promedio de completación
        completed_tasks_with_time = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.completed_at.isnot(None),
            Task.created_at.isnot(None)
        ).all()
        
        avg_completion_time = 0
        if completed_tasks_with_time:
            total_hours = 0
            for task in completed_tasks_with_time:
                time_diff = task.completed_at - task.created_at
                total_hours += time_diff.total_seconds() / 3600
            avg_completion_time = total_hours / len(completed_tasks_with_time)
        
        # Tareas más urgentes (vencidas)
        urgent_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.due_date < date.today(),
            Task.status.in_(["pending", "in_progress"])
        ).order_by(Task.due_date).limit(5).all()
        
        return {
            "status_distribution": [
                {"status": stat.status, "count": stat.count}
                for stat in status_stats
            ],
            "monthly_trend": [
                {
                    "month": f"{stat.year}-{stat.month:02d}",
                    "count": stat.count
                }
                for stat in monthly_stats
            ],
            "avg_completion_time_hours": round(avg_completion_time, 2),
            "urgent_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": task.due_date,
                    "priority": task.priority
                }
                for task in urgent_tasks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting tasks analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/chat")
async def get_chat_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener analytics del chat"""
    try:
        # Por ahora, como no tenemos un modelo de conversaciones,
        # retornamos estadísticas básicas
        # En el futuro, esto se conectaría con un modelo de conversaciones
        
        return {
            "total_conversations": 0,
            "messages_today": 0,
            "most_common_intents": [
                {"intent": "task_management", "count": 0},
                {"intent": "habit_tracking", "count": 0},
                {"intent": "productivity_advice", "count": 0}
            ],
            "average_response_time": 0,
            "user_satisfaction": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting chat analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/insights")
async def get_productivity_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener insights de productividad usando IA"""
    try:
        # Recopilar datos del usuario para análisis
        user_data = {
            "tasks_completed": db.query(Task).filter(
                Task.user_id == current_user.id,
                Task.status == "completed"
            ).count(),
            "habits_active": db.query(Habit).filter(
                Habit.user_id == current_user.id,
                Habit.is_active == True
            ).count(),
            "hours_focused": 0,  # Esto se calcularía con datos de sesiones de trabajo
            "activity_pattern": "regular"
        }
        
        # Generar insights usando el servicio de IA
        insights = ai_service.get_productivity_insights(user_data)
        
        return {
            "insights": insights,
            "user_data": user_data
        }
        
    except Exception as e:
        logger.error(f"Error getting productivity insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen general de analytics"""
    try:
        # Estadísticas generales
        total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
        completed_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status == "completed"
        ).count()
        
        total_habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
        active_habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True
        ).count()
        
        # Completaciones de hoy
        today = date.today()
        today_task_completions = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status == "completed",
            Task.completed_at >= today
        ).count()
        
        today_habit_completions = db.query(HabitLog).join(Habit).filter(
            Habit.user_id == current_user.id,
            HabitLog.completed_at >= today
        ).count()
        
        # Tareas vencidas
        overdue_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.due_date < date.today(),
            Task.status.in_(["pending", "in_progress"])
        ).count()
        
        return {
            "overview": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "total_habits": total_habits,
                "active_habits": active_habits
            },
            "today": {
                "task_completions": today_task_completions,
                "habit_completions": today_habit_completions
            },
            "alerts": {
                "overdue_tasks": overdue_tasks
            },
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
