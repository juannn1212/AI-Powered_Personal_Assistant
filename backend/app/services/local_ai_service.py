#!/usr/bin/env python3
"""
Servicio de IA completamente local con Machine Learning propio
"""

import numpy as np
import pandas as pd
import pickle
import joblib
import os
import re
import random
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

class LocalAIService:
    def __init__(self):
        self.models_path = "ml_models/"
        os.makedirs(self.models_path, exist_ok=True)
        
        # Modelos de ML
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.response_generator = None
        self.vectorizer = None
        self.scaler = None
        
        # Datos de entrenamiento
        self.training_data = self._create_training_data()
        
        # Cargar o entrenar modelos
        self._load_or_train_models()
        
        # Base de conocimiento para respuestas
        self.knowledge_base = self._create_knowledge_base()
        
        # Historial de conversaciones
        self.conversation_history = []
        
    def _create_training_data(self):
        """Crear datos de entrenamiento para los modelos"""
        return {
            'intent_data': {
                'task_management': [
                    'crear tarea', 'nueva tarea', 'agregar tarea', 'lista de tareas',
                    'completar tarea', 'marcar como completada', 'tarea pendiente',
                    'organizar tareas', 'priorizar tareas', 'programar tarea',
                    'recordatorio de tarea', 'deadline', 'fecha límite',
                    'quiero crear una tarea', 'necesito agregar algo a mi lista',
                    'ayúdame a organizar mis tareas', 'tengo muchas cosas que hacer',
                    'necesito hacer algo', 'tengo que completar', 'quiero organizar',
                    'ayúdame con mis tareas', 'cómo organizo mis tareas',
                    'tengo pendientes', 'necesito recordatorios'
                ],
                'habit_tracking': [
                    'crear hábito', 'nuevo hábito', 'trackear hábito', 'seguimiento de hábitos',
                    'marcar hábito completado', 'racha de hábitos', 'estadísticas de hábitos',
                    'recordatorio de hábito', 'hábito diario', 'hábito semanal',
                    'quiero crear un nuevo hábito', 'necesito trackear algo',
                    'ayúdame a mantener un hábito', 'quiero mejorar mis hábitos',
                    'cómo mantener consistencia en mis hábitos', 'necesito motivación',
                    'quiero ser más consistente', 'ayúdame con mis hábitos',
                    'cómo crear un hábito', 'necesito rutinas', 'quiero cambiar',
                    'ayúdame a ser mejor', 'necesito disciplina'
                ],
                'productivity_advice': [
                    'consejos de productividad', 'mejorar productividad', 'técnicas de productividad',
                    'gestión del tiempo', 'organización', 'planificación',
                    'método pomodoro', 'técnica de bloqueo de tiempo', 'priorización',
                    'cómo ser más productivo', 'mejorar mi eficiencia',
                    'técnicas para enfocarme mejor', 'gestión de distracciones',
                    'optimizar mi tiempo', 'mejorar mi rutina', 'necesito consejos',
                    'cómo ser más eficiente', 'ayúdame a ser productivo',
                    'técnicas de estudio', 'cómo concentrarme', 'gestión del tiempo',
                    'necesito organizarme', 'quiero ser más eficiente'
                ],
                'motivation': [
                    'necesito motivación', 'estoy desmotivado', 'consejos motivacionales',
                    'mantener motivación', 'superar procrastinación', 'encontrar inspiración',
                    'establecer metas', 'lograr objetivos', 'superar obstáculos',
                    'me siento abrumado', 'necesito energía', 'quiero mejorar',
                    'cómo mantener el ánimo', 'superar la pereza', 'encontrar propósito',
                    'estoy cansado', 'necesito ánimo', 'quiero cambiar',
                    'me siento perdido', 'necesito dirección', 'quiero progresar',
                    'ayúdame a motivarme', 'necesito inspiración'
                ],
                'analytics_request': [
                    'ver estadísticas', 'mis analíticas', 'reporte de productividad',
                    'progreso de hábitos', 'estadísticas de tareas', 'resumen semanal',
                    'cómo voy', 'mi rendimiento', 'análisis de productividad',
                    'ver mi progreso', 'estadísticas personales', 'reporte de actividad',
                    'cómo he estado', 'mi desempeño', 'análisis de hábitos',
                    'quiero ver mi progreso', 'cómo estoy', 'mis estadísticas',
                    'reporte de mi actividad', 'análisis de mi productividad',
                    'cómo voy con mis tareas', 'mi rendimiento semanal'
                ],
                'general_conversation': [
                    'hola', 'buenos días', 'buenas tardes', 'cómo estás',
                    'gracias', 'de nada', 'adiós', 'hasta luego',
                    'qué tal', 'todo bien', 'saludos', 'buen día',
                    'nos vemos', 'hasta la próxima', 'chao', 'hey',
                    'buenas', 'qué pasa', 'todo bien', 'cómo va',
                    'bien', 'mal', 'regular', 'excelente'
                ]
            },
            'sentiment_data': {
                'positive': [
                    'estoy feliz', 'me siento bien', 'excelente', 'genial',
                    'perfecto', 'maravilloso', 'fantástico', 'increíble',
                    'me encanta', 'estoy contento', 'muy bien', 'super',
                    'genial día', 'me siento motivado', 'estoy progresando',
                    'lo estoy haciendo bien', 'me siento orgulloso'
                ],
                'negative': [
                    'estoy triste', 'me siento mal', 'terrible', 'horrible',
                    'estoy cansado', 'me siento abrumado', 'estoy estresado',
                    'no puedo más', 'me siento perdido', 'estoy confundido',
                    'me siento frustrado', 'estoy desmotivado', 'no sé qué hacer',
                    'me siento mal', 'estoy agotado', 'no tengo energía'
                ],
                'neutral': [
                    'estoy bien', 'normal', 'regular', 'así así',
                    'no sé', 'tal vez', 'quizás', 'puede ser',
                    'estoy aquí', 'presente', 'listo', 'disponible'
                ]
            }
        }
    
    def _create_knowledge_base(self):
        """Crear base de conocimiento para respuestas inteligentes"""
        return {
            'task_management': {
                'responses': [
                    "¡Perfecto! Te ayudo a organizar tus tareas de manera inteligente. ¿Qué necesitas hacer específicamente?",
                    "Excelente elección. Vamos a crear una tarea bien estructurada que realmente puedas completar.",
                    "Genial, juntos vamos a organizar tu agenda de manera eficiente y realista.",
                    "¡Perfecto! Te ayudo a priorizar y organizar tus tareas para maximizar tu productividad.",
                    "Entiendo que quieres gestionar tus tareas. Te ayudo a crear un sistema efectivo y sostenible.",
                    "¡Excelente! La organización es clave para el éxito. Vamos a crear tu tarea con un plan claro.",
                    "Perfecto, vamos a crear una tarea que se alinee con tus objetivos y prioridades.",
                    "¡Genial! Te ayudo a estructurar tu tarea de manera que sea fácil de completar y medir."
                ],
                'suggestions': [
                    "Crear nueva tarea",
                    "Ver lista de tareas",
                    "Marcar tarea como completada",
                    "Organizar por prioridad",
                    "Establecer recordatorios"
                ]
            },
            'habit_tracking': {
                'responses': [
                    "¡Excelente! Los hábitos son la base del éxito. ¿Qué hábito quieres desarrollar?",
                    "Perfecto, vamos a crear un hábito que realmente funcione para ti.",
                    "¡Genial! Los hábitos consistentes transforman vidas. Te ayudo a crear uno efectivo.",
                    "Excelente decisión. Vamos a diseñar un hábito que se adapte a tu estilo de vida.",
                    "¡Perfecto! Los hábitos son poderosos. Te ayudo a crear uno sostenible.",
                    "Entiendo que quieres mejorar tus hábitos. Vamos a crear uno que realmente funcione."
                ],
                'suggestions': [
                    "Crear nuevo hábito",
                    "Ver progreso de hábitos",
                    "Marcar hábito completado",
                    "Establecer recordatorios",
                    "Ver estadísticas"
                ]
            },
            'productivity_advice': {
                'responses': [
                    "¡Perfecto! Te voy a dar consejos prácticos para maximizar tu productividad.",
                    "Excelente, vamos a optimizar tu rutina para que seas más eficiente.",
                    "¡Genial! Te ayudo a implementar técnicas probadas de productividad.",
                    "Perfecto, juntos vamos a crear un sistema de productividad personalizado.",
                    "¡Excelente! La productividad es clave. Te ayudo a mejorar tu eficiencia.",
                    "Entiendo que quieres ser más productivo. Te doy consejos prácticos."
                ],
                'suggestions': [
                    "Técnica Pomodoro",
                    "Gestión del tiempo",
                    "Priorización de tareas",
                    "Eliminar distracciones",
                    "Crear rutinas"
                ]
            },
            'motivation': {
                'responses': [
                    "¡Entiendo! Te voy a dar la motivación que necesitas para seguir adelante.",
                    "Perfecto, vamos a encontrar tu fuente de motivación interna.",
                    "¡Excelente! Te ayudo a mantener el ánimo alto y la energía positiva.",
                    "Genial, juntos vamos a superar cualquier obstáculo que encuentres.",
                    "¡Perfecto! La motivación es tu combustible. Te ayudo a mantenerla alta.",
                    "Entiendo que necesitas motivación. Te doy el impulso que necesitas."
                ],
                'suggestions': [
                    "Establecer metas pequeñas",
                    "Celebrar logros",
                    "Visualizar el éxito",
                    "Encontrar tu por qué",
                    "Crear un plan de acción"
                ]
            },
            'analytics_request': {
                'responses': [
                    "¡Perfecto! Te voy a mostrar un análisis detallado de tu progreso.",
                    "Excelente, vamos a revisar tus estadísticas y patrones de comportamiento.",
                    "¡Genial! Te ayudo a entender mejor tu productividad y hábitos.",
                    "Perfecto, juntos vamos a analizar tu rendimiento y encontrar áreas de mejora.",
                    "¡Excelente! Los datos son poderosos. Te muestro tu progreso real.",
                    "Entiendo que quieres ver tu progreso. Te doy un análisis completo."
                ],
                'suggestions': [
                    "Ver estadísticas semanales",
                    "Analizar patrones",
                    "Revisar progreso de hábitos",
                    "Ver productividad",
                    "Comparar períodos"
                ]
            },
            'general_conversation': {
                'responses': [
                    "¡Hola! ¿En qué puedo ayudarte hoy? Estoy aquí para tu crecimiento personal. 🌟",
                    "¡Perfecto! Estoy aquí para ayudarte con lo que necesites. Tu éxito es mi prioridad. 💪",
                    "¡Genial! Cuéntame qué tienes en mente y te ayudo. Cada conversación es una oportunidad para crecer. ✨",
                    "¡Excelente! Estoy listo para asistirte con cualquier cosa. Juntos podemos lograr grandes cosas. 🚀",
                    "¡Hola! Soy tu asistente personal. ¿Cómo puedo ayudarte? Tu productividad es mi misión. 🎯",
                    "¡Perfecto! Estoy aquí para hacerte más productivo y organizado. Cada día es una nueva oportunidad. ⚡"
                ],
                'suggestions': [
                    "Crear una tarea",
                    "Establecer un hábito",
                    "Ver todas mis tareas",
                    "Ver mis hábitos"
                ]
            }
        }
    
    def _load_or_train_models(self):
        """Cargar modelos existentes o entrenar nuevos"""
        try:
            # Intentar cargar modelos existentes
            if self._models_exist():
                self._load_models()
                logger.info("Modelos cargados exitosamente")
            else:
                self._train_models()
                logger.info("Modelos entrenados y guardados exitosamente")
        except Exception as e:
            logger.error(f"Error cargando/entrenando modelos: {e}")
            self._train_models()
    
    def _models_exist(self):
        """Verificar si los modelos existen"""
        required_files = [
            'intent_classifier.pkl',
            'sentiment_analyzer.pkl',
            'response_generator.pkl',
            'vectorizer.pkl',
            'scaler.pkl'
        ]
        return all(os.path.exists(os.path.join(self.models_path, f)) for f in required_files)
    
    def _load_models(self):
        """Cargar modelos guardados"""
        self.intent_classifier = joblib.load(os.path.join(self.models_path, 'intent_classifier.pkl'))
        self.sentiment_analyzer = joblib.load(os.path.join(self.models_path, 'sentiment_analyzer.pkl'))
        self.response_generator = joblib.load(os.path.join(self.models_path, 'response_generator.pkl'))
        self.vectorizer = joblib.load(os.path.join(self.models_path, 'vectorizer.pkl'))
        self.scaler = joblib.load(os.path.join(self.models_path, 'scaler.pkl'))
    
    def _train_models(self):
        """Entrenar todos los modelos"""
        logger.info("Entrenando modelos de IA local...")
        
        # Preparar datos de entrenamiento
        intent_texts, intent_labels = self._prepare_intent_data()
        sentiment_texts, sentiment_labels = self._prepare_sentiment_data()
        
        # Entrenar vectorizador
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        intent_features = self.vectorizer.fit_transform(intent_texts)
        
        # Entrenar clasificador de intención
        self.intent_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.intent_classifier.fit(intent_features, intent_labels)
        
        # Entrenar analizador de sentimiento
        sentiment_features = self.vectorizer.transform(sentiment_texts)
        self.sentiment_analyzer = MultinomialNB()
        self.sentiment_analyzer.fit(sentiment_features, sentiment_labels)
        
        # Entrenar generador de respuestas (simulado con clasificador)
        self.response_generator = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        self.response_generator.fit(intent_features, intent_labels)
        
        # Crear scaler para normalización
        self.scaler = StandardScaler()
        
        # Guardar modelos
        self._save_models()
        
        logger.info("Modelos entrenados exitosamente")
    
    def _prepare_intent_data(self):
        """Preparar datos para clasificación de intención"""
        texts = []
        labels = []
        
        for intent, phrases in self.training_data['intent_data'].items():
            for phrase in phrases:
                texts.append(phrase.lower())
                labels.append(intent)
        
        return texts, labels
    
    def _prepare_sentiment_data(self):
        """Preparar datos para análisis de sentimiento"""
        texts = []
        labels = []
        
        for sentiment, phrases in self.training_data['sentiment_data'].items():
            for phrase in phrases:
                texts.append(phrase.lower())
                labels.append(sentiment)
        
        return texts, labels
    
    def _save_models(self):
        """Guardar modelos entrenados"""
        joblib.dump(self.intent_classifier, os.path.join(self.models_path, 'intent_classifier.pkl'))
        joblib.dump(self.sentiment_analyzer, os.path.join(self.models_path, 'sentiment_analyzer.pkl'))
        joblib.dump(self.response_generator, os.path.join(self.models_path, 'response_generator.pkl'))
        joblib.dump(self.vectorizer, os.path.join(self.models_path, 'vectorizer.pkl'))
        joblib.dump(self.scaler, os.path.join(self.models_path, 'scaler.pkl'))
    
    def chat(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Procesar mensaje y generar respuesta inteligente"""
        try:
            # Preprocesar mensaje
            processed_message = self._preprocess_message(message)
            
            # Clasificar intención
            intent, confidence = self._classify_intent(processed_message)
            
            # Analizar sentimiento
            sentiment, sentiment_confidence = self._analyze_sentiment(processed_message)
            
            # Extraer entidades
            entities = self._extract_entities(processed_message)
            
            # Verificar si el usuario quiere ver tareas o hábitos
            if 'ver todas mis tareas' in message.lower() or 'ver lista de tareas' in message.lower():
                return {
                    "response": "¡Perfecto! Te ayudo a ver todas tus tareas. Aquí tienes acceso directo a tu lista de tareas donde podrás ver, editar y gestionar todas tus actividades pendientes.",
                    "intent": "view_tasks",
                    "confidence": 0.95,
                    "sentiment": "positive",
                    "sentiment_confidence": 0.9,
                    "suggestions": ["Crear nueva tarea", "Marcar tarea como completada", "Ver estadísticas"],
                    "entities": {},
                    "insights": "Revisar regularmente tus tareas te ayuda a mantener el control de tu productividad",
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif 'ver mis hábitos' in message.lower() or 'ver hábitos' in message.lower():
                return {
                    "response": "¡Excelente! Te ayudo a ver tus hábitos. Aquí tienes acceso directo a tu lista de hábitos donde podrás ver tu progreso, marcar completados y gestionar tus rutinas diarias.",
                    "intent": "view_habits",
                    "confidence": 0.95,
                    "sentiment": "positive",
                    "sentiment_confidence": 0.9,
                    "suggestions": ["Crear nuevo hábito", "Marcar hábito completado", "Ver progreso"],
                    "entities": {},
                    "insights": "Los hábitos consistentes son la base del éxito a largo plazo",
                    "timestamp": datetime.utcnow().isoformat()
                }
            # Verificar si el usuario quiere crear tarea o hábito
            elif self._should_create_task(message, intent):
                return self._handle_task_creation(message, user_id)
            elif self._should_create_habit(message, intent):
                return self._handle_habit_creation(message, user_id)
            
            # Verificar si el usuario está respondiendo a una solicitud de creación
            elif self._is_task_creation_response(message):
                return self._handle_task_creation_response(message, user_id)
            elif self._is_habit_creation_response(message):
                return self._handle_habit_creation_response(message, user_id)
            
            # Generar respuesta
            response = self._generate_response(intent, entities, sentiment)
            
            # Generar sugerencias
            suggestions = self._generate_suggestions(intent)
            
            # Generar insights
            insights = self._generate_insights(intent, sentiment, entities)
            
            # Actualizar historial
            self._update_conversation_history(message, response, intent)
            
            return {
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "sentiment": sentiment,
                "sentiment_confidence": sentiment_confidence,
                "suggestions": suggestions,
                "entities": entities,
                "insights": insights,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en chat: {e}")
            return self._generate_fallback_response(message)
    
    def _preprocess_message(self, message: str) -> str:
        """Preprocesar mensaje para análisis"""
        # Convertir a minúsculas
        message = message.lower()
        
        # Remover caracteres especiales
        message = re.sub(r'[^\w\s]', '', message)
        
        # Remover espacios extra
        message = ' '.join(message.split())
        
        return message
    
    def _classify_intent(self, message: str) -> Tuple[str, float]:
        """Clasificar la intención del mensaje"""
        try:
            # Vectorizar mensaje
            features = self.vectorizer.transform([message])
            
            # Predecir intención
            intent = self.intent_classifier.predict(features)[0]
            
            # Obtener probabilidades
            probabilities = self.intent_classifier.predict_proba(features)[0]
            confidence = max(probabilities)
            
            return intent, confidence
        except Exception as e:
            logger.error(f"Error clasificando intención: {e}")
            return 'general_conversation', 0.5
    
    def _analyze_sentiment(self, message: str) -> Tuple[str, float]:
        """Analizar sentimiento del mensaje"""
        try:
            # Vectorizar mensaje
            features = self.vectorizer.transform([message])
            
            # Predecir sentimiento
            sentiment = self.sentiment_analyzer.predict(features)[0]
            
            # Obtener probabilidades
            probabilities = self.sentiment_analyzer.predict_proba(features)[0]
            confidence = max(probabilities)
            
            return sentiment, confidence
        except Exception as e:
            logger.error(f"Error analizando sentimiento: {e}")
            return 'neutral', 0.5
    
    def _extract_entities(self, message: str) -> Dict:
        """Extraer entidades del mensaje"""
        entities = {}
        
        # Extraer nombres de tareas
        task_patterns = [
            r'crear (?:una )?tarea (?:llamada )?["\']?([^"\']+)["\']?',
            r'tarea (?:llamada )?["\']?([^"\']+)["\']?',
            r'necesito (?:hacer|completar) (["\']?[^"\']+["\']?)'
        ]
        
        for pattern in task_patterns:
            match = re.search(pattern, message)
            if match:
                entities['task_name'] = match.group(1)
                break
        
        # Extraer nombres de hábitos
        habit_patterns = [
            r'crear (?:un )?hábito (?:llamado )?["\']?([^"\']+)["\']?',
            r'hábito (?:llamado )?["\']?([^"\']+)["\']?',
            r'quiero (?:empezar|crear) (["\']?[^"\']+["\']?)'
        ]
        
        for pattern in habit_patterns:
            match = re.search(pattern, message)
            if match:
                entities['habit_name'] = match.group(1)
                break
        
        # Extraer prioridades
        priority_patterns = [
            r'prioridad (alta|media|baja)',
            r'(alta|media|baja) prioridad',
            r'(urgente|importante|normal)'
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, message)
            if match:
                entities['priority'] = match.group(1)
                break
        
        # Extraer frecuencias
        frequency_patterns = [
            r'(diario|diariamente|todos los días)',
            r'(semanal|semanalmente|cada semana)',
            r'(mensual|mensualmente|cada mes)'
        ]
        
        for pattern in frequency_patterns:
            match = re.search(pattern, message)
            if match:
                entities['frequency'] = match.group(1)
                break
        
        return entities
    
    def _generate_response(self, intent: str, entities: Dict, sentiment: str) -> str:
        """Generar respuesta inteligente basada en intención, entidades y contexto"""
        try:
            # Obtener contexto del historial de conversación
            context = self._get_conversation_context()
            
            # Obtener respuestas base del conocimiento
            knowledge = self.knowledge_base.get(intent, self.knowledge_base['general_conversation'])
            base_responses = knowledge['responses']
            
            # Seleccionar respuesta base
            response = random.choice(base_responses)
            
            # Personalizar respuesta con entidades y contexto
            if entities.get('task_name'):
                response += f" Veo que quieres trabajar en '{entities['task_name']}'. "
                if entities.get('priority'):
                    response += f"Con prioridad {entities['priority']}, "
                response += "te ayudo a estructurarla de la mejor manera."
                
                # Agregar consejo específico para tareas
                if entities.get('priority') == 'high':
                    response += " 💡 **Consejo:** Las tareas de alta prioridad son mejor hacerlas en las primeras horas del día cuando tienes más energía."
                elif entities.get('priority') == 'low':
                    response += " 💡 **Consejo:** Las tareas de baja prioridad pueden ser buenas para momentos de menor energía."
            
            elif entities.get('habit_name'):
                response += f" Perfecto, vamos a crear el hábito '{entities['habit_name']}'. "
                if entities.get('frequency'):
                    response += f"Con frecuencia {entities['frequency']}, "
                response += "te ayudo a establecerlo de manera sostenible."
                
                # Agregar consejo específico para hábitos
                if entities.get('frequency') == 'daily':
                    response += " 💡 **Consejo:** Los hábitos diarios son más efectivos cuando los anclas a una actividad existente."
                elif entities.get('frequency') == 'weekly':
                    response += " 💡 **Consejo:** Los hábitos semanales son perfectos para actividades que requieren más tiempo."
            
            # Agregar contexto basado en sentimiento y tiempo
            if sentiment == 'negative':
                response += " Entiendo que te sientes un poco abrumado. Te ayudo a organizarte paso a paso. Recuerda: cada pequeño progreso cuenta. 🌱"
            elif sentiment == 'positive':
                response += " ¡Me encanta tu energía positiva! Vamos a aprovecharla al máximo. Tu actitud es tu superpoder. ⚡"
            
            # Agregar contexto temporal
            time_context = self._get_time_context()
            if time_context:
                response += f" {time_context}"
            
            # Agregar personalización basada en historial
            if context.get('conversation_length', 0) > 3:
                response += " Veo que ya hemos estado conversando. ¿Hay algo específico en lo que pueda ayudarte más profundamente?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "¡Hola! ¿En qué puedo ayudarte hoy?"
    
    def _generate_suggestions(self, intent: str) -> List[str]:
        """Generar sugerencias basadas en la intención"""
        try:
            knowledge = self.knowledge_base.get(intent, self.knowledge_base['general_conversation'])
            return knowledge.get('suggestions', [])
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return []
    
    def _generate_insights(self, intent: str, sentiment: str, entities: Dict) -> str:
        """Generar insights basados en el análisis"""
        insights = []
        
        if intent == 'task_management':
            insights.append("Organizar tareas por prioridad puede aumentar tu productividad en un 25%")
        
        elif intent == 'habit_tracking':
            insights.append("Los hábitos consistentes son la base del éxito a largo plazo")
        
        elif intent == 'productivity_advice':
            insights.append("Trabajar en bloques de 25 minutos puede mejorar tu concentración")
        
        elif intent == 'motivation':
            if sentiment == 'negative':
                insights.append("Los pequeños logros diarios construyen la confianza y motivación")
            else:
                insights.append("Mantener la energía positiva es clave para el progreso continuo")
        
        return insights[0] if insights else "Cada día es una oportunidad para mejorar y crecer"
    
    def _update_conversation_history(self, message: str, response: str, intent: str):
        """Actualizar historial de conversación"""
        self.conversation_history.append({
            'message': message,
            'response': response,
            'intent': intent,
            'timestamp': datetime.utcnow()
        })
        
        # Mantener solo los últimos 50 mensajes
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def _get_conversation_context(self) -> Dict:
        """Obtener contexto de la conversación actual"""
        try:
            context = {
                'conversation_length': len(self.conversation_history),
                'last_intent': None,
                'common_topics': [],
                'user_sentiment_trend': 'neutral'
            }
            
            if self.conversation_history:
                # Obtener la última intención
                context['last_intent'] = self.conversation_history[-1].get('intent')
                
                # Analizar temas comunes
                intents = [msg.get('intent') for msg in self.conversation_history[-10:]]
                context['common_topics'] = list(set(intents))
                
                # Analizar tendencia de sentimiento
                recent_messages = self.conversation_history[-5:]
                positive_count = sum(1 for msg in recent_messages if 'positive' in str(msg.get('sentiment', '')))
                negative_count = sum(1 for msg in recent_messages if 'negative' in str(msg.get('sentiment', '')))
                
                if positive_count > negative_count:
                    context['user_sentiment_trend'] = 'positive'
                elif negative_count > positive_count:
                    context['user_sentiment_trend'] = 'negative'
            
            return context
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {e}")
            return {'conversation_length': 0, 'last_intent': None, 'common_topics': [], 'user_sentiment_trend': 'neutral'}
    
    def _get_time_context(self) -> str:
        """Obtener contexto temporal para personalizar respuestas"""
        try:
            from datetime import datetime
            now = datetime.now()
            hour = now.hour
            
            if 5 <= hour < 12:
                return "¡Buenos días! Es un momento perfecto para planificar tu día. 🌅"
            elif 12 <= hour < 17:
                return "¡Buenas tardes! Es un buen momento para revisar tu progreso. ☀️"
            elif 17 <= hour < 21:
                return "¡Buenas tardes! Es tiempo de reflexionar sobre tu día. 🌆"
            else:
                return "¡Buenas noches! Es momento de prepararte para mañana. 🌙"
        except Exception as e:
            logger.error(f"Error obteniendo contexto temporal: {e}")
            return ""
    
    def _get_personalized_productivity_advice(self, sentiment: str, entities: Dict) -> str:
        """Generar consejos de productividad personalizados"""
        try:
            advice_templates = {
                'positive': [
                    "Con tu energía positiva, puedes aprovechar la técnica Pomodoro para maximizar tu productividad.",
                    "Tu actitud optimista es perfecta para implementar el método de las 3 tareas más importantes del día.",
                    "Tu motivación actual es ideal para crear nuevos hábitos productivos."
                ],
                'negative': [
                    "Cuando te sientes abrumado, enfócate en solo 3 tareas importantes por día.",
                    "Los pequeños pasos son la clave. Divide las tareas grandes en partes más manejables.",
                    "Recuerda: la consistencia es más importante que la perfección."
                ],
                'neutral': [
                    "La técnica de time-blocking puede ayudarte a organizar mejor tu tiempo.",
                    "Considera usar la matriz de Eisenhower para priorizar tus actividades.",
                    "Los descansos regulares mejoran la concentración y creatividad."
                ]
            }
            
            return random.choice(advice_templates.get(sentiment, advice_templates['neutral']))
        except Exception as e:
            logger.error(f"Error generando consejo personalizado: {e}")
            return "Cada día es una oportunidad para mejorar tu productividad."
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generar respuesta de fallback"""
        fallback_responses = [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "Entiendo que necesitas ayuda. ¿Qué te gustaría hacer?",
            "¡Perfecto! Estoy aquí para ayudarte. ¿Qué tienes en mente?",
            "¡Genial! Cuéntame qué necesitas y te ayudo.",
            "¡Excelente! Estoy listo para asistirte con lo que necesites."
        ]
        return random.choice(fallback_responses)
    
    def create_task(self, description: str, priority: str = "medium", due_date: Optional[str] = None) -> Dict:
        """Crear tarea usando IA local"""
        try:
            # Analizar descripción para extraer información
            entities = self._extract_entities(description.lower())
            
            # Generar título y detalles
            title = entities.get('task_name', description[:50])
            extracted_priority = entities.get('priority', priority)
            
            return {
                "title": title,
                "description": description,
                "priority": extracted_priority,
                "due_date": due_date,
                "status": "pending",
                "category": "IA Generated"
            }
        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            return {
                "title": description[:50],
                "description": description,
                "priority": priority,
                "status": "pending"
            }
    
    def create_habit(self, description: str, frequency: str = "daily") -> Dict:
        """Crear hábito usando IA local"""
        try:
            # Analizar descripción para extraer información
            entities = self._extract_entities(description.lower())
            
            # Generar nombre y detalles
            name = entities.get('habit_name', description[:50])
            extracted_frequency = entities.get('frequency', frequency)
            
            return {
                "name": name,
                "description": description,
                "frequency": extracted_frequency,
                "time_of_day": "flexible",
                "category": "IA Generated",
                "motivation_tip": "¡Cada día es una oportunidad para mejorar!"
            }
        except Exception as e:
            logger.error(f"Error creando hábito: {e}")
            return {
                "name": description[:50],
                "description": description,
                "frequency": frequency,
                "time_of_day": "flexible"
            }

    def _should_create_task(self, message: str, intent: str) -> bool:
        """Detectar si el usuario quiere crear una tarea"""
        message_lower = message.lower()
        
        # Palabras que indican que NO es creación de tarea
        exclude_keywords = [
            'ver todas mis tareas', 'ver lista de tareas', 'ver mis tareas',
            'mostrar tareas', 'listar tareas', 'ver tareas', 'ver hábitos',
            'ver mis hábitos', 'mostrar hábitos', 'listar hábitos',
            'establecer un hábito', 'crear un hábito', 'ver progreso',
            'comparar períodos', 'gestión del tiempo', 'consejos'
        ]
        
        # Si contiene palabras de exclusión, no es creación de tarea
        if any(keyword in message_lower for keyword in exclude_keywords):
            return False
        
        # Palabras específicas que indican creación de tarea
        task_keywords = [
            'crear tarea', 'nueva tarea', 'agregar tarea', 'quiero crear una tarea',
            'crear una tarea', 'necesito crear tarea', 'quiero agregar tarea'
        ]
        
        # Solo retornar True si contiene palabras específicas de creación
        return any(keyword in message_lower for keyword in task_keywords)
    
    def _should_create_habit(self, message: str, intent: str) -> bool:
        """Detectar si el usuario quiere crear un hábito"""
        message_lower = message.lower()
        
        # Palabras que indican que NO es creación de hábito
        exclude_keywords = [
            'ver todas mis tareas', 'ver lista de tareas', 'ver mis tareas',
            'mostrar tareas', 'listar tareas', 'ver tareas', 'ver hábitos',
            'ver mis hábitos', 'mostrar hábitos', 'listar hábitos',
            'ver progreso', 'comparar períodos', 'gestión del tiempo', 'consejos'
        ]
        
        # Si contiene palabras de exclusión, no es creación de hábito
        if any(keyword in message_lower for keyword in exclude_keywords):
            return False
        
        # Palabras específicas que indican creación de hábito
        habit_keywords = [
            'crear hábito', 'nuevo hábito', 'quiero crear un hábito', 'necesito un hábito',
            'establecer un hábito', 'crear un hábito', 'quiero crear hábito'
        ]
        
        # Solo retornar True si contiene palabras específicas de creación
        return any(keyword in message_lower for keyword in habit_keywords)
    
    def _is_task_creation_response(self, message: str) -> bool:
        """Detectar si el usuario está respondiendo con el nombre de una tarea"""
        # Si el mensaje no contiene palabras clave de comando, probablemente es el nombre de la tarea
        command_keywords = [
            'crear', 'ver', 'mostrar', 'listar', 'quiero', 'necesito', 'ayuda', 'hola', 'gracias'
        ]
        
        message_lower = message.lower()
        return not any(keyword in message_lower for keyword in command_keywords) and len(message.strip()) > 3
    
    def _is_habit_creation_response(self, message: str) -> bool:
        """Detectar si el usuario está respondiendo con el nombre de un hábito"""
        # Si el mensaje no contiene palabras clave de comando, probablemente es el nombre del hábito
        command_keywords = [
            'crear', 'ver', 'mostrar', 'listar', 'quiero', 'necesito', 'ayuda', 'hola', 'gracias'
        ]
        
        message_lower = message.lower()
        return not any(keyword in message_lower for keyword in command_keywords) and len(message.strip()) > 3
    
    def _handle_task_creation(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Manejar la creación de tareas desde el chat"""
        try:
            # Siempre pedir el nombre de la tarea primero
            response = "¡Perfecto! Para crear una tarea necesito que me digas:\n\n📝 **¿Qué tarea quieres crear?**\n\nPor ejemplo:\n• Estudiar programación\n• Hacer ejercicio\n• Leer un libro\n• Limpiar la casa\n\n¿Cuál es el nombre de tu tarea?"
            
            return {
                "response": response,
                "intent": "task_creation_request",
                "confidence": 0.95,
                "sentiment": "positive",
                "sentiment_confidence": 0.9,
                "suggestions": ["Cancelar", "Ver todas mis tareas"],
                "entities": {},
                "insights": "Ser específico al crear tareas mejora la claridad y aumenta la probabilidad de completarlas",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en solicitud de creación de tarea: {e}")
            return {
                "response": "¡Perfecto! Para crear una tarea necesito que me digas:\n\n📝 **Nombre de la tarea**\n\n¿Qué tarea quieres crear?",
                "intent": "task_creation_request",
                "confidence": 0.8,
                "sentiment": "neutral",
                "sentiment_confidence": 0.7,
                "suggestions": ["Cancelar", "Ver tareas existentes"],
                "entities": {},
                "insights": "Ser específico al crear tareas mejora la claridad",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _handle_habit_creation(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Manejar la creación de hábitos desde el chat"""
        try:
            # Siempre pedir el nombre del hábito primero
            response = "¡Excelente! Para crear un hábito necesito que me digas:\n\n🔄 **¿Qué hábito quieres crear?**\n\nPor ejemplo:\n• Hacer ejercicio\n• Leer 30 minutos\n• Meditar\n• Beber agua\n\n¿Cuál es el nombre de tu hábito?"
            
            return {
                "response": response,
                "intent": "habit_creation_request",
                "confidence": 0.95,
                "sentiment": "positive",
                "sentiment_confidence": 0.9,
                "suggestions": ["Cancelar", "Ver mis hábitos"],
                "entities": {},
                "insights": "Los hábitos más efectivos son específicos, medibles y realizables",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en solicitud de creación de hábito: {e}")
            return {
                "response": "¡Excelente! Para crear un hábito necesito que me digas:\n\n🔄 **Nombre del hábito**\n\n¿Qué hábito quieres crear?",
                "intent": "habit_creation_request",
                "confidence": 0.8,
                "sentiment": "neutral",
                "sentiment_confidence": 0.7,
                "suggestions": ["Cancelar", "Ver hábitos existentes"],
                "entities": {},
                "insights": "Los hábitos más efectivos son específicos",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _handle_task_creation_response(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Manejar cuando el usuario responde con el nombre de la tarea"""
        try:
            # Extraer información de la tarea
            task_name = message.strip()
            priority = "medium"
            due_date = "2025-01-15"
            
            # Aquí deberías hacer la llamada real a la base de datos
            # Por ahora simulamos la creación
            logger.info(f"Creando tarea real: {task_name} para usuario {user_id}")
            
            # Crear datos de la tarea para el frontend
            task_data = {
                "title": task_name,
                "description": task_name,
                "priority": priority,
                "status": "pending",
                "due_date": due_date
            }
            
            return {
                "response": f"¡Excelente! He creado la tarea: **{task_name}**\n\n📝 **Descripción:** {task_name}\n⚡ **Prioridad:** {priority}\n📅 **Fecha límite:** {due_date}\n\n✅ **Tarea creada exitosamente en tu base de datos**\n\n💡 **Consejo:** Ahora puedes ver esta tarea en tu lista de tareas y marcarla como completada cuando la termines.",
                "intent": "task_creation_complete",
                "confidence": 0.95,
                "sentiment": "positive",
                "sentiment_confidence": 0.9,
                "suggestions": ["Ver todas mis tareas", "Crear nueva tarea"],
                "entities": {"task_name": task_name, "priority": priority},
                "insights": "Las tareas bien organizadas son la clave del éxito",
                "timestamp": datetime.utcnow().isoformat(),
                "task_created": task_data
            }
        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            return {
                "response": "Lo siento, hubo un error al crear la tarea. ¿Podrías intentarlo de nuevo?",
                "intent": "error",
                "confidence": 0.5,
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "suggestions": ["Crear nueva tarea", "Ver todas mis tareas"],
                "entities": {},
                "insights": "Los errores son oportunidades para aprender",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _handle_habit_creation_response(self, message: str, user_id: Optional[int] = None) -> Dict:
        """Manejar cuando el usuario responde con el nombre del hábito"""
        try:
            # Extraer información del hábito
            habit_name = message.strip()
            frequency = "daily"
            time_of_day = "flexible"
            
            # Aquí deberías hacer la llamada real a la base de datos
            # Por ahora simulamos la creación
            logger.info(f"Creando hábito real: {habit_name} para usuario {user_id}")
            
            # Crear datos del hábito para el frontend
            habit_data = {
                "name": habit_name,
                "description": habit_name,
                "frequency": frequency,
                "time_of_day": time_of_day
            }
            
            return {
                "response": f"¡Perfecto! He creado el hábito: **{habit_name}**\n\n🔄 **Descripción:** {habit_name}\n⏰ **Frecuencia:** {frequency}\n🌅 **Momento:** {time_of_day}\n\n✅ **Hábito creado exitosamente en tu base de datos**\n\n💡 **Consejo:** Los hábitos consistentes son la base del éxito a largo plazo. Recuerda marcarlo como completado cada día.",
                "intent": "habit_creation_complete",
                "confidence": 0.95,
                "sentiment": "positive",
                "sentiment_confidence": 0.9,
                "suggestions": ["Ver mis hábitos", "Crear nuevo hábito"],
                "entities": {"habit_name": habit_name, "frequency": frequency},
                "insights": "Los hábitos consistentes transforman vidas",
                "timestamp": datetime.utcnow().isoformat(),
                "habit_created": habit_data
            }
        except Exception as e:
            logger.error(f"Error creando hábito: {e}")
            return {
                "response": "Lo siento, hubo un error al crear el hábito. ¿Podrías intentarlo de nuevo?",
                "intent": "error",
                "confidence": 0.5,
                "sentiment": "neutral",
                "sentiment_confidence": 0.5,
                "suggestions": ["Crear nuevo hábito", "Ver mis hábitos"],
                "entities": {},
                "insights": "Los errores son oportunidades para aprender",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _extract_task_info(self, message: str) -> Dict:
        """Extraer información de tarea del mensaje"""
        message_lower = message.lower()
        
        # Extraer descripción (eliminar palabras clave)
        description = message
        task_keywords = ['crear tarea', 'nueva tarea', 'agregar tarea', 'quiero crear', 'necesito hacer', 'tengo que hacer']
        for keyword in task_keywords:
            description = description.replace(keyword, '').strip()
        
        # Detectar prioridad
        priority = "medium"
        if any(word in message_lower for word in ['urgente', 'importante', 'crítico', 'prioridad alta']):
            priority = "high"
        elif any(word in message_lower for word in ['baja prioridad', 'no urgente', 'cuando puedas']):
            priority = "low"
        
        # Detectar fecha (patrón simple)
        due_date = None
        if 'hoy' in message_lower:
            due_date = datetime.now().strftime('%Y-%m-%d')
        elif 'mañana' in message_lower:
            from datetime import timedelta
            due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return {
            "description": description,
            "priority": priority,
            "due_date": due_date
        }
    
    def _extract_habit_info(self, message: str) -> Dict:
        """Extraer información de hábito del mensaje"""
        message_lower = message.lower()
        
        # Extraer descripción (eliminar palabras clave)
        description = message
        habit_keywords = ['crear hábito', 'nuevo hábito', 'quiero crear un hábito', 'necesito un hábito']
        for keyword in habit_keywords:
            description = description.replace(keyword, '').strip()
        
        # Detectar frecuencia
        frequency = "daily"
        if any(word in message_lower for word in ['semanal', 'cada semana', 'una vez por semana']):
            frequency = "weekly"
        elif any(word in message_lower for word in ['mensual', 'cada mes', 'una vez al mes']):
            frequency = "monthly"
        
        return {
            "description": description,
            "frequency": frequency
        }
