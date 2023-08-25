import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import json
import os
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import re

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.intent_classifier = None
        self.vectorizer = None
        self.model_path = "./ml_models"
        self.intent_labels = [
            "task_management",
            "habit_tracking", 
            "productivity",
            "calendar",
            "analytics",
            "general"
        ]
        
        # Training data for intent classification
        self.training_data = {
            "task_management": [
                "crear tarea", "nueva tarea", "agregar tarea", "completar tarea",
                "marcar como completada", "lista de tareas", "tareas pendientes",
                "priorizar tareas", "organizar tareas", "recordatorio tarea",
                "create task", "new task", "add task", "complete task",
                "mark as done", "task list", "pending tasks", "prioritize tasks"
            ],
            "habit_tracking": [
                "crear hábito", "nuevo hábito", "seguimiento hábitos", "registrar hábito",
                "progreso hábitos", "estadísticas hábitos", "recordatorio hábito",
                "create habit", "new habit", "track habits", "log habit",
                "habit progress", "habit statistics", "habit reminder"
            ],
            "productivity": [
                "análisis productividad", "estadísticas productividad", "optimizar tiempo",
                "mejorar productividad", "consejos productividad", "rutina diaria",
                "productivity analysis", "productivity stats", "optimize time",
                "improve productivity", "productivity tips", "daily routine"
            ],
            "calendar": [
                "evento calendario", "nuevo evento", "reunión", "cita",
                "agenda", "horario", "programar", "calendar event",
                "new event", "meeting", "appointment", "schedule"
            ],
            "analytics": [
                "reporte", "estadísticas", "análisis", "métricas",
                "progreso", "tendencias", "report", "statistics",
                "analysis", "metrics", "progress", "trends"
            ],
            "general": [
                "hola", "buenos días", "buenas tardes", "ayuda", "información",
                "hello", "good morning", "good afternoon", "help", "info"
            ]
        }
        
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """
        Load existing model or train a new one
        """
        try:
            model_file = os.path.join(self.model_path, "intent_classifier.pkl")
            vectorizer_file = os.path.join(self.model_path, "vectorizer.pkl")
            
            if os.path.exists(model_file) and os.path.exists(vectorizer_file):
                self.intent_classifier = pickle.load(open(model_file, 'rb'))
                self.vectorizer = pickle.load(open(vectorizer_file, 'rb'))
                logger.info("Loaded existing ML model")
            else:
                self._train_intent_classifier()
                
        except Exception as e:
            logger.error(f"Error loading/training model: {e}")
            self._train_intent_classifier()
    
    def _train_intent_classifier(self):
        """
        Train the intent classification model
        """
        try:
            # Prepare training data
            texts = []
            labels = []
            
            for intent, phrases in self.training_data.items():
                for phrase in phrases:
                    texts.append(phrase.lower())
                    labels.append(intent)
            
            # Create and fit vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            X = self.vectorizer.fit_transform(texts)
            
            # Train classifier
            self.intent_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            self.intent_classifier.fit(X, labels)
            
            # Save model
            os.makedirs(self.model_path, exist_ok=True)
            pickle.dump(self.intent_classifier, open(os.path.join(self.model_path, "intent_classifier.pkl"), 'wb'))
            pickle.dump(self.vectorizer, open(os.path.join(self.model_path, "vectorizer.pkl"), 'wb'))
            
            logger.info("Trained and saved new ML model")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
    
    async def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message
        """
        try:
            if not self.intent_classifier or not self.vectorizer:
                return "general"
            
            # Preprocess message
            processed_message = self._preprocess_text(message)
            
            # Vectorize
            X = self.vectorizer.transform([processed_message])
            
            # Predict
            intent = self.intent_classifier.predict(X)[0]
            confidence = max(self.intent_classifier.predict_proba(X)[0])
            
            # Return general if confidence is too low
            if confidence < 0.3:
                return "general"
            
            return intent
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return "general"
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for ML model
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    async def analyze_user_patterns(self, user_data: List[Dict]) -> Dict:
        """
        Analyze user behavior patterns
        """
        try:
            if not user_data:
                return {}
            
            df = pd.DataFrame(user_data)
            
            patterns = {
                "productivity_trends": self._analyze_productivity_trends(df),
                "task_completion_patterns": self._analyze_task_patterns(df),
                "habit_consistency": self._analyze_habit_consistency(df),
                "time_analysis": self._analyze_time_patterns(df),
                "recommendations": self._generate_pattern_recommendations(df)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {}
    
    def _analyze_productivity_trends(self, df: pd.DataFrame) -> Dict:
        """
        Analyze productivity trends over time
        """
        try:
            if 'productivity_score' not in df.columns:
                return {}
            
            trends = {
                "average_score": float(df['productivity_score'].mean()),
                "trend": "stable",
                "best_day": None,
                "worst_day": None
            }
            
            # Calculate trend
            if len(df) > 1:
                recent_scores = df['productivity_score'].tail(7)
                if len(recent_scores) > 1:
                    slope = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
                    if slope > 0.1:
                        trends["trend"] = "improving"
                    elif slope < -0.1:
                        trends["trend"] = "declining"
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing productivity trends: {e}")
            return {}
    
    def _analyze_task_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze task completion patterns
        """
        try:
            if 'tasks_completed' not in df.columns:
                return {}
            
            patterns = {
                "average_tasks_per_day": float(df['tasks_completed'].mean()),
                "completion_rate": 0.0,
                "peak_hours": [],
                "difficulty_distribution": {}
            }
            
            # Calculate completion rate if we have task data
            if 'total_tasks' in df.columns:
                total_completed = df['tasks_completed'].sum()
                total_assigned = df['total_tasks'].sum()
                if total_assigned > 0:
                    patterns["completion_rate"] = total_completed / total_assigned
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing task patterns: {e}")
            return {}
    
    def _analyze_habit_consistency(self, df: pd.DataFrame) -> Dict:
        """
        Analyze habit consistency patterns
        """
        try:
            if 'habits_completed' not in df.columns:
                return {}
            
            consistency = {
                "average_habits_per_day": float(df['habits_completed'].mean()),
                "consistency_score": 0.0,
                "streak_analysis": {},
                "most_consistent_habit": None
            }
            
            # Calculate consistency score
            if len(df) > 0:
                total_days = len(df)
                days_with_habits = len(df[df['habits_completed'] > 0])
                consistency["consistency_score"] = days_with_habits / total_days
            
            return consistency
            
        except Exception as e:
            logger.error(f"Error analyzing habit consistency: {e}")
            return {}
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze time-based patterns
        """
        try:
            if 'time_spent_focused' not in df.columns:
                return {}
            
            time_analysis = {
                "average_focus_time": float(df['time_spent_focused'].mean()),
                "peak_productivity_hours": [],
                "time_distribution": {},
                "efficiency_score": 0.0
            }
            
            # Calculate efficiency score
            if 'productivity_score' in df.columns and 'time_spent_focused' in df.columns:
                productivity_per_hour = df['productivity_score'] / df['time_spent_focused']
                time_analysis["efficiency_score"] = float(productivity_per_hour.mean())
            
            return time_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing time patterns: {e}")
            return {}
    
    def _generate_pattern_recommendations(self, df: pd.DataFrame) -> List[str]:
        """
        Generate recommendations based on pattern analysis
        """
        recommendations = []
        
        try:
            # Productivity recommendations
            if 'productivity_score' in df.columns:
                avg_score = df['productivity_score'].mean()
                if avg_score < 6:
                    recommendations.append("Considera implementar técnicas de gestión del tiempo como Pomodoro")
                if avg_score < 5:
                    recommendations.append("Evalúa tu rutina matutina para mejorar tu productividad diaria")
            
            # Task completion recommendations
            if 'tasks_completed' in df.columns:
                avg_tasks = df['tasks_completed'].mean()
                if avg_tasks < 3:
                    recommendations.append("Intenta dividir tareas grandes en subtareas más manejables")
                if avg_tasks > 8:
                    recommendations.append("Considera priorizar mejor tus tareas para evitar el agotamiento")
            
            # Habit consistency recommendations
            if 'habits_completed' in df.columns:
                consistency = len(df[df['habits_completed'] > 0]) / len(df)
                if consistency < 0.7:
                    recommendations.append("Establece recordatorios más frecuentes para tus hábitos")
                if consistency < 0.5:
                    recommendations.append("Considera simplificar tus hábitos para aumentar la consistencia")
            
            # Time management recommendations
            if 'time_spent_focused' in df.columns:
                avg_focus = df['time_spent_focused'].mean()
                if avg_focus < 4:
                    recommendations.append("Dedica más tiempo a sesiones de trabajo enfocado")
                if avg_focus > 8:
                    recommendations.append("Asegúrate de tomar descansos regulares para mantener la productividad")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def predict_user_behavior(self, user_history: List[Dict]) -> Dict:
        """
        Predict future user behavior based on historical data
        """
        try:
            if len(user_history) < 7:
                return {"prediction": "insufficient_data"}
            
            df = pd.DataFrame(user_history)
            
            predictions = {
                "next_day_productivity": self._predict_productivity(df),
                "task_completion_forecast": self._predict_task_completion(df),
                "habit_success_probability": self._predict_habit_success(df),
                "optimal_work_hours": self._predict_optimal_hours(df)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting behavior: {e}")
            return {"prediction": "error"}
    
    def _predict_productivity(self, df: pd.DataFrame) -> float:
        """
        Predict next day's productivity score
        """
        try:
            if 'productivity_score' not in df.columns:
                return 5.0
            
            recent_scores = df['productivity_score'].tail(7).values
            
            # Simple moving average prediction
            prediction = np.mean(recent_scores)
            
            # Add trend component
            if len(recent_scores) > 1:
                trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
                prediction += trend * 0.5
            
            return max(0, min(10, prediction))
            
        except Exception as e:
            logger.error(f"Error predicting productivity: {e}")
            return 5.0
    
    def _predict_task_completion(self, df: pd.DataFrame) -> int:
        """
        Predict number of tasks to be completed next day
        """
        try:
            if 'tasks_completed' not in df.columns:
                return 3
            
            recent_tasks = df['tasks_completed'].tail(7).values
            prediction = int(np.mean(recent_tasks))
            
            return max(0, prediction)
            
        except Exception as e:
            logger.error(f"Error predicting task completion: {e}")
            return 3
    
    def _predict_habit_success(self, df: pd.DataFrame) -> float:
        """
        Predict probability of habit completion
        """
        try:
            if 'habits_completed' not in df.columns:
                return 0.5
            
            recent_habits = df['habits_completed'].tail(7).values
            success_rate = np.mean(recent_habits > 0)
            
            return min(1.0, max(0.0, success_rate))
            
        except Exception as e:
            logger.error(f"Error predicting habit success: {e}")
            return 0.5
    
    def _predict_optimal_hours(self, df: pd.DataFrame) -> List[int]:
        """
        Predict optimal working hours
        """
        try:
            # Default optimal hours (9 AM - 5 PM)
            return [9, 10, 11, 12, 13, 14, 15, 16, 17]
            
        except Exception as e:
            logger.error(f"Error predicting optimal hours: {e}")
            return [9, 10, 11, 12, 13, 14, 15, 16, 17]
