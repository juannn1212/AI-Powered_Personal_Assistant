#!/usr/bin/env python3
"""
Rutas para el asistente de IA con TensorFlow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.services.ai_service import AIService
from app.schemas.assistant import ChatRequest, ChatResponse
from app.models.user import User
from app.services.auth_service import get_current_user
from app.models.task import Task
from app.models.habit import Habit
from app.schemas.task import TaskCreate
from app.schemas.habit import HabitCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["assistant"])

# Inicializar servicio de IA
ai_service = AIService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat con el asistente de IA usando TensorFlow"""
    try:
        logger.info(f"🧠 Procesando mensaje de usuario {current_user.id}: {request.message[:50]}...")
        
        # Procesar mensaje con TensorFlow
        response = ai_service.process_message(
            message=request.message,
            user_id=str(current_user.id),
            user_context={"user_id": current_user.id, "email": current_user.email}
        )
        
        # Si la IA indica que se creó una tarea, crearla realmente en la base de datos
        if response.get('task_created'):
            logger.info(f"📝 Creando tarea en base de datos: {response['task_created']['title']}")
            
            task_data = response['task_created']
            task_create = TaskCreate(
                title=task_data['title'],
                description=task_data['description'],
                priority=task_data['priority'],
                status=task_data['status'],
                due_date=task_data.get('due_date'),
                user_id=current_user.id
            )
            
            db_task = Task(**task_create.dict())
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            
            logger.info(f"✅ Tarea creada exitosamente: {db_task.title} (ID: {db_task.id})")
        
        # Si la IA indica que se creó un hábito, crearlo realmente en la base de datos
        if response.get('habit_created'):
            logger.info(f"🔄 Creando hábito en base de datos: {response['habit_created']['name']}")
            
            habit_data = response['habit_created']
            habit_create = HabitCreate(
                name=habit_data['name'],
                description=habit_data['description'],
                frequency=habit_data['frequency'],
                time_of_day=habit_data.get('time_of_day', 'flexible'),
                user_id=current_user.id
            )
            
            db_habit = Habit(**habit_create.dict())
            db.add(db_habit)
            db.commit()
            db.refresh(db_habit)
            
            logger.info(f"✅ Hábito creado exitosamente: {db_habit.name} (ID: {db_habit.id})")
        
        logger.info(f"✅ Respuesta generada - Intención: {response.get('intent')}")
        
        return ChatResponse(
            success=True,
            message="Mensaje procesado exitosamente",
            data=response
        )
        
    except HTTPException as e:
        # Si es un error de autenticación, dar un mensaje más útil
        if e.status_code == 401:
            logger.warning(f"🔐 Sesión perdida para usuario: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tu sesión ha expirado. Por favor, vuelve a iniciar sesión para continuar usando el asistente."
            )
        else:
            raise e
    except Exception as e:
        logger.error(f"❌ Error en chat con asistente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando mensaje: {str(e)}"
        )

@router.get("/model-info")
async def get_model_info():
    """Obtener información del modelo de TensorFlow"""
    try:
        model_info = ai_service.get_model_info()
        return {
            "success": True,
            "message": "Información del modelo obtenida",
            "data": model_info
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo información del modelo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información del modelo: {str(e)}"
        )

@router.get("/health")
async def assistant_health():
    """Verificar estado del asistente de IA"""
    try:
        model_info = ai_service.get_model_info()
        is_healthy = model_info.get("status") in ["active", "fallback"]
        
        return {
            "success": True,
            "message": "Estado del asistente verificado",
            "data": {
                "status": "healthy" if is_healthy else "unhealthy",
                "model_info": model_info,
                "timestamp": "2025-01-15T00:00:00Z"
            }
        }
    except Exception as e:
        logger.error(f"❌ Error verificando salud del asistente: {e}")
        return {
            "success": False,
            "message": "Error verificando estado del asistente",
            "data": {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-15T00:00:00Z"
            }
        }
