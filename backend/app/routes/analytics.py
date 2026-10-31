from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Any, Dict
import logging

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.habit import Habit, HabitLog
from app.models.chat_message import ChatMessage
from app.services.auth_service import get_current_user
from app.services.analytics_service import compute_analytics

logger = logging.getLogger(__name__)

router = APIRouter()


def _load(db: Session, user: User, period: str, tz_offset: int) -> Dict[str, Any]:
    tasks = db.query(Task).filter(Task.user_id == user.id).all()
    habits = db.query(Habit).filter(Habit.user_id == user.id).all()
    habit_ids = [h.id for h in habits]
    logs = db.query(HabitLog).filter(HabitLog.habit_id.in_(habit_ids)).all() if habit_ids else []
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).all()
    return compute_analytics(tasks, habits, logs, messages, period=period, tz_offset=tz_offset)


def _section(name: str):
    """Crea un endpoint que devuelve una sección del cálculo de analíticas."""
    async def endpoint(
        period: str = Query("week", description="week | month | year"),
        tz_offset: int = Query(0, ge=-840, le=840, description="Minutos al este de UTC del dispositivo"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        try:
            data = _load(db, current_user, period, tz_offset)
            if name == "insights":
                return {"insights": data["insights"], "period": data["period"]}
            return data[name]
        except Exception as e:
            logger.error(f"Error calculando analytics/{name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor",
            )
    endpoint.__name__ = f"analytics_{name}"
    return endpoint


for _name in ("summary", "productivity", "tasks", "habits", "chat", "insights"):
    router.add_api_route(f"/{_name}", _section(_name), methods=["GET"])
