from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from app.database import get_db, User, Conversation, Task, Habit, UserAnalytics
from app.services.ai_service import AIService
from app.services.auth_service import get_current_user
from app.utils.logger import logger

router = APIRouter()
ai_service = AIService()

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict] = None

class MessageResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    sentiment: str
    suggestions: List[str]
    timestamp: datetime

class ConversationHistory(BaseModel):
    id: int
    message: str
    response: str
    intent: str
    confidence: float
    created_at: datetime

@router.post("/chat", response_model=MessageResponse)
async def chat_with_assistant(
    request: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with the AI assistant
    """
    try:
        # Get user context
        user_context = await _get_user_context(current_user, db)
        
        # Process message with AI
        ai_response = await ai_service.process_message(
            message=request.message,
            user_context=user_context,
            intent=request.context.get("intent") if request.context else None
        )
        
        # Save conversation to database
        conversation = Conversation(
            user_id=current_user.id,
            message=request.message,
            response=ai_response["response"],
            intent=ai_response["intent"],
            confidence=ai_response["confidence"]
        )
        db.add(conversation)
        db.commit()
        
        return MessageResponse(
            response=ai_response["response"],
            intent=ai_response["intent"],
            confidence=ai_response["confidence"],
            sentiment=ai_response["sentiment"],
            suggestions=ai_response["suggestions"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationHistory])
async def get_conversation_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation history for the current user
    """
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
        
        return [
            ConversationHistory(
                id=conv.id,
                message=conv.message,
                response=conv.response,
                intent=conv.intent,
                confidence=conv.confidence,
                created_at=conv.created_at
            )
            for conv in conversations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )

@router.post("/suggestions/tasks")
async def get_task_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered task suggestions
    """
    try:
        # Get user's current tasks
        user_tasks = db.query(Task).filter(
            Task.user_id == current_user.id,
            Task.status.in_(["pending", "in_progress"])
        ).all()
        
        task_data = [
            {
                "title": task.title,
                "description": task.description,
                "priority": task.priority
            }
            for task in user_tasks
        ]
        
        # Generate suggestions
        suggestions = await ai_service.generate_task_suggestions(task_data)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating task suggestions: {str(e)}"
        )

@router.get("/analytics/productivity")
async def analyze_productivity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered productivity analysis
    """
    try:
        # Get user analytics data
        analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id
        ).order_by(UserAnalytics.date.desc()).limit(30).all()
        
        analytics_data = [
            {
                "date": str(anal.date),
                "productivity_score": anal.productivity_score,
                "tasks_completed": anal.tasks_completed,
                "habits_completed": anal.habits_completed,
                "time_spent_focused": anal.time_spent_focused,
                "mood_score": anal.mood_score
            }
            for anal in analytics
        ]
        
        # Analyze patterns
        analysis = await ai_service.analyze_productivity_patterns(analytics_data)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing productivity: {str(e)}"
        )

@router.post("/voice/transcribe")
async def transcribe_voice(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe voice message to text
    """
    try:
        # Save audio file temporarily
        temp_file = f"temp_audio_{current_user.id}_{datetime.now().timestamp()}.wav"
        
        with open(temp_file, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        # TODO: Implement voice transcription
        # For now, return a placeholder
        transcribed_text = "Transcripción de voz no implementada aún"
        
        # Clean up temp file
        os.remove(temp_file)
        
        return {"transcribed_text": transcribed_text}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing voice: {str(e)}"
        )

@router.get("/intent/analyze")
async def analyze_intent(
    message: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the intent of a message
    """
    try:
        intent = await ai_service.ml_service.classify_intent(message)
        
        return {
            "message": message,
            "intent": intent,
            "confidence": 0.8  # Placeholder confidence
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing intent: {str(e)}"
        )

async def _get_user_context(user: User, db: Session) -> Dict:
    """
    Get user context for AI processing
    """
    try:
        context = {}
        
        # Get recent tasks
        recent_tasks = db.query(Task).filter(
            Task.user_id == user.id,
            Task.status.in_(["pending", "in_progress"])
        ).limit(5).all()
        
        context["recent_tasks"] = [task.title for task in recent_tasks]
        
        # Get active habits
        active_habits = db.query(Habit).filter(
            Habit.user_id == user.id,
            Habit.is_active == True
        ).all()
        
        context["habits"] = [habit.name for habit in active_habits]
        
        # Get latest productivity score
        latest_analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == user.id
        ).order_by(UserAnalytics.date.desc()).first()
        
        if latest_analytics:
            context["productivity_score"] = latest_analytics.productivity_score
            context["mood"] = f"{latest_analytics.mood_score}/10"
        
        return context
        
    except Exception as e:
        logger.error(f"Error getting user context: {e}")
        return {}
