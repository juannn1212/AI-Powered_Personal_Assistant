import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import logging
from typing import Dict, List, Optional, Tuple
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.models_path = "ml_models/"
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.vectorizer = None
        self.load_models()
        
        # Intent categories
        self.intent_categories = [
            'task_management',
            'habit_tracking', 
            'productivity_advice',
            'motivation',
            'general_conversation',
            'analytics_request',
            'profile_management'
        ]
        
        # Training data for intent classification
        self.intent_training_data = {
            'task_management': [
                'crear tarea', 'nueva tarea', 'agregar tarea', 'lista de tareas',
                'completar tarea', 'marcar como completada', 'tarea pendiente',
                'organizar tareas', 'priorizar tareas', 'programar tarea',
                'recordatorio de tarea', 'deadline', 'fecha límite',
                'quiero crear una tarea', 'necesito agregar algo a mi lista',
                'ayúdame a organizar mis tareas', 'tengo muchas cosas que hacer'
            ],
            'habit_tracking': [
                'crear hábito', 'nuevo hábito', 'trackear hábito', 'seguimiento de hábitos',
                'marcar hábito completado', 'racha de hábitos', 'estadísticas de hábitos',
                'recordatorio de hábito', 'hábito diario', 'hábito semanal',
                'quiero crear un nuevo hábito', 'necesito trackear algo',
                'ayúdame a mantener un hábito', 'quiero mejorar mis hábitos',
                'cómo mantener consistencia en mis hábitos'
            ],
            'productivity_advice': [
                'consejos de productividad', 'mejorar productividad', 'técnicas de productividad',
                'gestión del tiempo', 'organización', 'planificación',
                'método pomodoro', 'técnica de bloqueo de tiempo', 'priorización',
                'cómo ser más productivo', 'mejorar mi eficiencia',
                'técnicas para enfocarme mejor', 'gestión de distracciones',
                'optimizar mi tiempo', 'mejorar mi rutina'
            ],
            'motivation': [
                'necesito motivación', 'estoy desmotivado', 'consejos motivacionales',
                'mantener motivación', 'superar procrastinación', 'encontrar inspiración',
                'establecer metas', 'lograr objetivos', 'superar obstáculos',
                'me siento abrumado', 'necesito energía', 'quiero mejorar',
                'cómo mantener el ánimo', 'superar la pereza', 'encontrar propósito'
            ],
            'analytics_request': [
                'ver estadísticas', 'mis analíticas', 'reporte de productividad',
                'progreso de hábitos', 'estadísticas de tareas', 'resumen semanal',
                'cómo voy', 'mi rendimiento', 'análisis de productividad',
                'ver mi progreso', 'estadísticas personales', 'reporte de actividad',
                'cómo he estado', 'mi desempeño', 'análisis de hábitos'
            ],
            'profile_management': [
                'cambiar perfil', 'editar información', 'actualizar datos',
                'cambiar contraseña', 'configuración de cuenta', 'preferencias',
                'modo oscuro', 'notificaciones', 'configuración',
                'mi perfil', 'datos personales', 'ajustes de cuenta',
                'personalización', 'configurar app', 'preferencias de usuario'
            ],
            'general_conversation': [
                'hola', 'buenos días', 'buenas tardes', 'cómo estás',
                'gracias', 'de nada', 'adiós', 'hasta luego',
                'qué tal', 'todo bien', 'saludos', 'buen día',
                'nos vemos', 'hasta la próxima', 'chao'
            ]
        }
        
        # Train models if they don't exist
        if not self.models_exist():
            self.train_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            # Load intent classifier
            intent_path = os.path.join(self.models_path, "intent_classifier.pkl")
            if os.path.exists(intent_path):
                self.intent_classifier = joblib.load(intent_path)
                logger.info("Intent classifier loaded successfully")
            
            # Load sentiment analyzer
            sentiment_path = os.path.join(self.models_path, "sentiment_analyzer.pkl")
            if os.path.exists(sentiment_path):
                self.sentiment_analyzer = joblib.load(sentiment_path)
                logger.info("Sentiment analyzer loaded successfully")
            
            # Load vectorizer
            vectorizer_path = os.path.join(self.models_path, "vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info("Vectorizer loaded successfully")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def models_exist(self) -> bool:
        """Check if all models exist"""
        required_files = [
            "intent_classifier.pkl",
            "sentiment_analyzer.pkl", 
            "vectorizer.pkl"
        ]
        
        for file in required_files:
            if not os.path.exists(os.path.join(self.models_path, file)):
                return False
        return True
    
    def train_models(self):
        """Train all ML models"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(self.models_path, exist_ok=True)
            
            # Prepare training data
            texts = []
            intents = []
            
            for intent, phrases in self.intent_training_data.items():
                for phrase in phrases:
                    texts.append(phrase)
                    intents.append(intent)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                texts, intents, test_size=0.2, random_state=42
            )
            
            # Create and train vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            X_train_vectorized = self.vectorizer.fit_transform(X_train)
            X_test_vectorized = self.vectorizer.transform(X_test)
            
            # Train intent classifier
            self.intent_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            self.intent_classifier.fit(X_train_vectorized, y_train)
            
            # Train sentiment analyzer
            self.sentiment_analyzer = MultinomialNB()
            # For sentiment, we'll use a simple approach based on keywords
            sentiment_labels = self._generate_sentiment_labels(texts)
            self.sentiment_analyzer.fit(X_train_vectorized, sentiment_labels)
            
            # Save models
            joblib.dump(self.intent_classifier, os.path.join(self.models_path, "intent_classifier.pkl"))
            joblib.dump(self.sentiment_analyzer, os.path.join(self.models_path, "sentiment_analyzer.pkl"))
            joblib.dump(self.vectorizer, os.path.join(self.models_path, "vectorizer.pkl"))
            
            # Evaluate models
            intent_accuracy = accuracy_score(y_test, self.intent_classifier.predict(X_test_vectorized))
            sentiment_accuracy = accuracy_score(
                self._generate_sentiment_labels(X_test), 
                self.sentiment_analyzer.predict(X_test_vectorized)
            )
            
            logger.info(f"Intent classifier accuracy: {intent_accuracy:.2f}")
            logger.info(f"Sentiment analyzer accuracy: {sentiment_accuracy:.2f}")
            logger.info("Models trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
    
    def _generate_sentiment_labels(self, texts: List[str]) -> List[str]:
        """Generate sentiment labels based on keywords"""
        positive_words = ['gracias', 'excelente', 'genial', 'perfecto', 'bueno', 'mejor', 'feliz', 'contento']
        negative_words = ['malo', 'terrible', 'horrible', 'triste', 'enojado', 'frustrado', 'molesto', 'cansado']
        
        labels = []
        for text in texts:
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                labels.append('positive')
            elif negative_count > positive_count:
                labels.append('negative')
            else:
                labels.append('neutral')
        
        return labels
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent of a text message"""
        try:
            if not self.intent_classifier or not self.vectorizer:
                return 'general_conversation', 0.5
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Vectorize text
            text_vectorized = self.vectorizer.transform([processed_text])
            
            # Predict intent
            intent = self.intent_classifier.predict(text_vectorized)[0]
            
            # Get confidence score
            confidence = max(self.intent_classifier.predict_proba(text_vectorized)[0])
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return 'general_conversation', 0.5
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze the sentiment of a text message"""
        try:
            if not self.sentiment_analyzer or not self.vectorizer:
                return 'neutral', 0.5
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Vectorize text
            text_vectorized = self.vectorizer.transform([processed_text])
            
            # Predict sentiment
            sentiment = self.sentiment_analyzer.predict(text_vectorized)[0]
            
            # Get confidence score
            confidence = max(self.sentiment_analyzer.predict_proba(text_vectorized)[0])
            
            return sentiment, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return 'neutral', 0.5
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text (tasks, habits, dates, etc.)"""
        entities = {}
        
        try:
            # Extract task-related entities
            task_patterns = [
                r'crear (?:una )?tarea (?:llamada )?["\']?([^"\']+)["\']?',
                r'nueva tarea (?:llamada )?["\']?([^"\']+)["\']?',
                r'agregar (?:una )?tarea (?:llamada )?["\']?([^"\']+)["\']?',
                r'tarea (?:llamada )?["\']?([^"\']+)["\']?'
            ]
            
            for pattern in task_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities['task_name'] = match.group(1).strip()
                    break
            
            # Extract habit-related entities
            habit_patterns = [
                r'crear (?:un )?h[áa]bito (?:llamado )?["\']?([^"\']+)["\']?',
                r'nuevo h[áa]bito (?:llamado )?["\']?([^"\']+)["\']?',
                r'h[áa]bito (?:llamado )?["\']?([^"\']+)["\']?'
            ]
            
            for pattern in habit_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities['habit_name'] = match.group(1).strip()
                    break
            
            # Extract priority
            priority_patterns = {
                'alta': ['alta prioridad', 'urgente', 'importante', 'crítico'],
                'media': ['media prioridad', 'normal', 'regular'],
                'baja': ['baja prioridad', 'poco importante', 'opcional']
            }
            
            for priority, keywords in priority_patterns.items():
                if any(keyword in text.lower() for keyword in keywords):
                    entities['priority'] = priority
                    break
            
            # Extract frequency for habits
            frequency_patterns = {
                'diario': ['diario', 'cada día', 'todos los días', 'diariamente'],
                'semanal': ['semanal', 'cada semana', 'una vez por semana'],
                'mensual': ['mensual', 'cada mes', 'una vez al mes']
            }
            
            for frequency, keywords in frequency_patterns.items():
                if any(keyword in text.lower() for keyword in keywords):
                    entities['frequency'] = frequency
                    break
            
            # Extract dates
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
                r'(hoy|mañana|pasado mañana)',
                r'(lunes|martes|miércoles|jueves|viernes|sábado|domingo)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities['date'] = match.group(1)
                    break
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
        
        return entities
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for ML models"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_suggestions(self, intent: str, context: Dict = None) -> List[str]:
        """Get contextual suggestions based on intent"""
        suggestions = {
            'task_management': [
                '¿Quieres que te ayude a crear una nueva tarea?',
                '¿Te gustaría establecer prioridades para tus tareas?',
                '¿Necesitas ayuda para organizar tu agenda?',
                '¿Quieres que programe recordatorios para tus tareas?'
            ],
            'habit_tracking': [
                '¿Quieres crear un nuevo hábito?',
                '¿Te gustaría revisar tus hábitos actuales?',
                '¿Necesitas motivación para mantener tus hábitos?',
                '¿Quieres ver estadísticas de tus hábitos?'
            ],
            'productivity_advice': [
                '¿Quieres aprender técnicas de productividad?',
                '¿Te gustaría analizar cómo usas tu tiempo?',
                '¿Necesitas ayuda para evitar distracciones?',
                '¿Quieres que te ayude a optimizar tu rutina?'
            ],
            'motivation': [
                '¿Quieres que te ayude a encontrar motivación?',
                '¿Te gustaría establecer metas específicas?',
                '¿Necesitas consejos para superar la procrastinación?',
                '¿Quieres que analicemos qué te motiva?'
            ],
            'analytics_request': [
                '¿Quieres ver tu progreso de esta semana?',
                '¿Te gustaría analizar tus patrones de productividad?',
                '¿Necesitas un reporte de tus hábitos?',
                '¿Quieres comparar tu rendimiento con semanas anteriores?'
            ],
            'profile_management': [
                '¿Quieres actualizar tu información personal?',
                '¿Te gustaría cambiar la configuración de notificaciones?',
                '¿Necesitas ayuda con la configuración de la app?',
                '¿Quieres personalizar tu experiencia?'
            ],
            'general_conversation': [
                '¿En qué puedo ayudarte hoy?',
                '¿Quieres que revise tus tareas pendientes?',
                '¿Te gustaría que analice tu productividad?',
                '¿Necesitas ayuda con algo específico?'
            ]
        }
        
        return suggestions.get(intent, suggestions['general_conversation'])
    
    def analyze_user_patterns(self, user_data: List[Dict]) -> Dict:
        """Analyze user behavior patterns"""
        try:
            if not user_data:
                return {}
            
            analysis = {
                'productivity_trend': 'stable',
                'peak_hours': [],
                'consistency_score': 0.0,
                'improvement_areas': [],
                'strengths': []
            }
            
            # Analyze productivity trend
            if len(user_data) >= 2:
                recent_scores = [d.get('productivity_score', 0) for d in user_data[-7:]]
                if len(recent_scores) >= 2:
                    trend = recent_scores[-1] - recent_scores[0]
                    if trend > 1:
                        analysis['productivity_trend'] = 'improving'
                    elif trend < -1:
                        analysis['productivity_trend'] = 'declining'
            
            # Analyze consistency
            if user_data:
                scores = [d.get('productivity_score', 0) for d in user_data]
                if scores:
                    mean_score = np.mean(scores)
                    std_score = np.std(scores)
                    consistency = max(0, 1 - (std_score / mean_score)) if mean_score > 0 else 0
                    analysis['consistency_score'] = consistency
            
            # Identify strengths and areas for improvement
            if user_data:
                avg_tasks = np.mean([d.get('tasks_completed', 0) for d in user_data])
                avg_habits = np.mean([d.get('habits_completed', 0) for d in user_data])
                
                if avg_tasks > 5:
                    analysis['strengths'].append('Completas muchas tareas diariamente')
                if avg_habits > 2:
                    analysis['strengths'].append('Mantienes buenos hábitos')
                
                if avg_tasks < 3:
                    analysis['improvement_areas'].append('Podrías completar más tareas por día')
                if avg_habits < 1:
                    analysis['improvement_areas'].append('Podrías mejorar la consistencia en hábitos')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {str(e)}")
            return {}
    
    def predict_user_behavior(self, user_data: List[Dict]) -> Dict:
        """Predict user behavior based on historical data"""
        try:
            if not user_data or len(user_data) < 7:
                return {}
            
            predictions = {
                'next_week_productivity': 0.0,
                'task_completion_prediction': 0,
                'habit_success_probability': 0.0,
                'recommended_actions': []
            }
            
            # Simple prediction based on recent trends
            recent_scores = [d.get('productivity_score', 0) for d in user_data[-7:]]
            if recent_scores:
                predictions['next_week_productivity'] = np.mean(recent_scores)
            
            recent_tasks = [d.get('tasks_completed', 0) for d in user_data[-7:]]
            if recent_tasks:
                predictions['task_completion_prediction'] = int(np.mean(recent_tasks))
            
            recent_habits = [d.get('habits_completed', 0) for d in user_data[-7:]]
            if recent_habits:
                avg_habits = np.mean(recent_habits)
                predictions['habit_success_probability'] = min(1.0, avg_habits / 5.0)
            
            # Generate recommendations
            if predictions['next_week_productivity'] < 6:
                predictions['recommended_actions'].append('Considera implementar técnicas de gestión del tiempo')
            
            if predictions['task_completion_prediction'] < 3:
                predictions['recommended_actions'].append('Intenta dividir tareas grandes en subtareas más pequeñas')
            
            if predictions['habit_success_probability'] < 0.5:
                predictions['recommended_actions'].append('Establece recordatorios más frecuentes para tus hábitos')
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting user behavior: {str(e)}")
            return {}
