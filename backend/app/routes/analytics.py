from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime, date, timedelta

from app.database import get_db, User, UserAnalytics, Task, Habit
from app.routes.auth import get_current_active_user
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

# Pydantic models
class AnalyticsData(BaseModel):
    date: date
    productivity_score: float
    tasks_completed: int
    habits_completed: int
    time_spent_focused: float
    mood_score: float

class AnalyticsResponse(BaseModel):
    daily_data: List[AnalyticsData]
    summary: Dict
    trends: Dict
    recommendations: List[str]

class ProductivityInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    value: float
    trend: str

@router.post("/track", response_model=AnalyticsData)
async def track_daily_analytics(
    analytics_data: AnalyticsData,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Track daily productivity analytics
    """
    try:
        # Check if analytics already exists for today
        existing_analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id,
            UserAnalytics.date == analytics_data.date
        ).first()
        
        if existing_analytics:
            # Update existing analytics
            existing_analytics.productivity_score = analytics_data.productivity_score
            existing_analytics.tasks_completed = analytics_data.tasks_completed
            existing_analytics.habits_completed = analytics_data.habits_completed
            existing_analytics.time_spent_focused = analytics_data.time_spent_focused
            existing_analytics.mood_score = analytics_data.mood_score
        else:
            # Create new analytics entry
            new_analytics = UserAnalytics(
                user_id=current_user.id,
                date=analytics_data.date,
                productivity_score=analytics_data.productivity_score,
                tasks_completed=analytics_data.tasks_completed,
                habits_completed=analytics_data.habits_completed,
                time_spent_focused=analytics_data.time_spent_focused,
                mood_score=analytics_data.mood_score
            )
            db.add(new_analytics)
        
        db.commit()
        
        return analytics_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking analytics: {str(e)}"
        )

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard
    """
    try:
        # Get analytics data for the specified period
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id,
            UserAnalytics.date >= start_date,
            UserAnalytics.date <= end_date
        ).order_by(UserAnalytics.date).all()
        
        # Convert to Pydantic models
        daily_data = [
            AnalyticsData(
                date=anal.date,
                productivity_score=anal.productivity_score,
                tasks_completed=anal.tasks_completed,
                habits_completed=anal.habits_completed,
                time_spent_focused=anal.time_spent_focused,
                mood_score=anal.mood_score
            )
            for anal in analytics
        ]
        
        # Calculate summary statistics
        summary = _calculate_summary(daily_data)
        
        # Analyze trends
        trends = _analyze_trends(daily_data)
        
        # Generate recommendations
        recommendations = await _generate_recommendations(daily_data)
        
        return AnalyticsResponse(
            daily_data=daily_data,
            summary=summary,
            trends=trends,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )

@router.get("/insights", response_model=List[ProductivityInsight])
async def get_productivity_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered productivity insights
    """
    try:
        # Get recent analytics data
        analytics = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id
        ).order_by(UserAnalytics.date.desc()).limit(30).all()
        
        # Convert to format for ML analysis
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
        
        # Analyze patterns using ML service
        patterns = await ml_service.analyze_user_patterns(analytics_data)
        
        # Generate insights
        insights = _generate_insights(patterns, analytics_data)
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )

@router.get("/predictions")
async def get_productivity_predictions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get productivity predictions using ML
    """
    try:
        # Get historical data
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
        
        # Get predictions
        predictions = await ml_service.predict_user_behavior(analytics_data)
        
        return predictions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating predictions: {str(e)}"
        )

@router.get("/comparison")
async def compare_periods(
    period1_start: date,
    period1_end: date,
    period2_start: date,
    period2_end: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compare productivity between two time periods
    """
    try:
        # Get data for both periods
        period1_data = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id,
            UserAnalytics.date >= period1_start,
            UserAnalytics.date <= period1_end
        ).all()
        
        period2_data = db.query(UserAnalytics).filter(
            UserAnalytics.user_id == current_user.id,
            UserAnalytics.date >= period2_start,
            UserAnalytics.date <= period2_end
        ).all()
        
        # Calculate averages for each period
        period1_avg = _calculate_period_averages(period1_data)
        period2_avg = _calculate_period_averages(period2_data)
        
        # Calculate improvements/declines
        comparison = {
            "period1": period1_avg,
            "period2": period2_avg,
            "changes": {
                "productivity_score": period2_avg["productivity_score"] - period1_avg["productivity_score"],
                "tasks_completed": period2_avg["tasks_completed"] - period1_avg["tasks_completed"],
                "habits_completed": period2_avg["habits_completed"] - period1_avg["habits_completed"],
                "time_spent_focused": period2_avg["time_spent_focused"] - period1_avg["time_spent_focused"],
                "mood_score": period2_avg["mood_score"] - period1_avg["mood_score"]
            }
        }
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing periods: {str(e)}"
        )

def _calculate_summary(daily_data: List[AnalyticsData]) -> Dict:
    """Calculate summary statistics"""
    if not daily_data:
        return {}
    
    productivity_scores = [d.productivity_score for d in daily_data]
    tasks_completed = [d.tasks_completed for d in daily_data]
    habits_completed = [d.habits_completed for d in daily_data]
    time_spent = [d.time_spent_focused for d in daily_data]
    mood_scores = [d.mood_score for d in daily_data]
    
    return {
        "avg_productivity": sum(productivity_scores) / len(productivity_scores),
        "total_tasks": sum(tasks_completed),
        "total_habits": sum(habits_completed),
        "total_focus_time": sum(time_spent),
        "avg_mood": sum(mood_scores) / len(mood_scores),
        "best_day": max(daily_data, key=lambda x: x.productivity_score).date,
        "most_productive_day": max(daily_data, key=lambda x: x.tasks_completed).date
    }

def _analyze_trends(daily_data: List[AnalyticsData]) -> Dict:
    """Analyze trends in the data"""
    if len(daily_data) < 2:
        return {"trend": "insufficient_data"}
    
    # Calculate trend for productivity score
    productivity_scores = [d.productivity_score for d in daily_data]
    if len(productivity_scores) > 1:
        trend_slope = (productivity_scores[-1] - productivity_scores[0]) / len(productivity_scores)
        if trend_slope > 0.1:
            trend = "improving"
        elif trend_slope < -0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "consistency_score": _calculate_consistency(daily_data),
        "peak_performance_days": _find_peak_days(daily_data)
    }

def _calculate_consistency(daily_data: List[AnalyticsData]) -> float:
    """Calculate consistency score"""
    if not daily_data:
        return 0.0
    
    # Calculate standard deviation of productivity scores
    scores = [d.productivity_score for d in daily_data]
    mean_score = sum(scores) / len(scores)
    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    std_dev = variance ** 0.5
    
    # Lower standard deviation = higher consistency
    consistency = max(0, 1 - (std_dev / 10))
    return consistency

def _find_peak_days(daily_data: List[AnalyticsData]) -> List[date]:
    """Find days with peak performance"""
    if not daily_data:
        return []
    
    # Find days with productivity score > 8
    peak_days = [d.date for d in daily_data if d.productivity_score >= 8]
    return peak_days

async def _generate_recommendations(daily_data: List[AnalyticsData]) -> List[str]:
    """Generate personalized recommendations"""
    if not daily_data:
        return ["Comienza a registrar tu productividad para recibir recomendaciones personalizadas"]
    
    recommendations = []
    
    # Analyze average productivity
    avg_productivity = sum(d.productivity_score for d in daily_data) / len(daily_data)
    if avg_productivity < 6:
        recommendations.append("Tu productividad promedio es baja. Considera implementar técnicas de gestión del tiempo.")
    
    # Analyze task completion
    avg_tasks = sum(d.tasks_completed for d in daily_data) / len(daily_data)
    if avg_tasks < 3:
        recommendations.append("Completas pocas tareas por día. Intenta dividir tareas grandes en subtareas más pequeñas.")
    
    # Analyze habit consistency
    days_with_habits = len([d for d in daily_data if d.habits_completed > 0])
    habit_consistency = days_with_habits / len(daily_data)
    if habit_consistency < 0.7:
        recommendations.append("Tu consistencia en hábitos es baja. Establece recordatorios más frecuentes.")
    
    # Analyze focus time
    avg_focus = sum(d.time_spent_focused for d in daily_data) / len(daily_data)
    if avg_focus < 4:
        recommendations.append("Dedicas poco tiempo al trabajo enfocado. Considera usar la técnica Pomodoro.")
    
    return recommendations[:5]

def _generate_insights(patterns: Dict, analytics_data: List[Dict]) -> List[ProductivityInsight]:
    """Generate productivity insights"""
    insights = []
    
    if not analytics_data:
        return insights
    
    # Calculate averages
    avg_productivity = sum(d["productivity_score"] for d in analytics_data) / len(analytics_data)
    avg_tasks = sum(d["tasks_completed"] for d in analytics_data) / len(analytics_data)
    avg_habits = sum(d["habits_completed"] for d in analytics_data) / len(analytics_data)
    avg_focus = sum(d["time_spent_focused"] for d in analytics_data) / len(analytics_data)
    
    # Generate insights based on patterns
    if patterns.get("productivity_trends", {}).get("trend") == "improving":
        insights.append(ProductivityInsight(
            insight_type="trend",
            title="Productividad en Aumento",
            description="Tu productividad ha mejorado en las últimas semanas",
            value=avg_productivity,
            trend="up"
        ))
    
    if avg_tasks < 3:
        insights.append(ProductivityInsight(
            insight_type="opportunity",
            title="Oportunidad de Mejora",
            description="Podrías completar más tareas por día",
            value=avg_tasks,
            trend="stable"
        ))
    
    if avg_focus < 4:
        insights.append(ProductivityInsight(
            insight_type="focus",
            title="Tiempo de Enfoque",
            description="Considera dedicar más tiempo al trabajo enfocado",
            value=avg_focus,
            trend="down"
        ))
    
    return insights

def _calculate_period_averages(period_data: List) -> Dict:
    """Calculate averages for a time period"""
    if not period_data:
        return {
            "productivity_score": 0,
            "tasks_completed": 0,
            "habits_completed": 0,
            "time_spent_focused": 0,
            "mood_score": 0
        }
    
    return {
        "productivity_score": sum(d.productivity_score for d in period_data) / len(period_data),
        "tasks_completed": sum(d.tasks_completed for d in period_data) / len(period_data),
        "habits_completed": sum(d.habits_completed for d in period_data) / len(period_data),
        "time_spent_focused": sum(d.time_spent_focused for d in period_data) / len(period_data),
        "mood_score": sum(d.mood_score for d in period_data) / len(period_data)
    }
