#!/usr/bin/env python3
"""
Servicio de IA con TensorFlow - Sistema de Machine Learning Real
"""

import tensorflow as tf
import numpy as np
import pandas as pd
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

logger = logging.getLogger(__name__)

class TensorFlowAIService:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.conversation_history = []
        self.user_context = {}
        self.model_path = "ai_model"
        self.vectorizer_path = "vectorizer.pkl"
        self.label_encoder_path = "label_encoder.pkl"
        
        # Datos de entrenamiento para el modelo
        self.training_data = self._create_training_data()
        
        # Inicializar el modelo
        self._initialize_model()
    
    def _create_training_data(self) -> List[Dict]:
        """Crear datos de entrenamiento para el modelo de ML"""
        return [
            # Saludos y conversación general
            {"text": "hola", "intent": "greeting", "response": "¡Hola! ¿Cómo te sientes hoy? Estoy aquí para escucharte."},
            {"text": "buenos días", "intent": "greeting", "response": "¡Buenos días! ¿Cómo va tu día? Estoy aquí para acompañarte."},
            {"text": "buenas tardes", "intent": "greeting", "response": "¡Buenas tardes! ¿Cómo te sientes? Cuéntame qué pasa por tu mente."},
            {"text": "buenas noches", "intent": "greeting", "response": "¡Buenas noches! ¿Cómo te sientes al final de este día?"},
            {"text": "como estas", "intent": "greeting", "response": "¡Muy bien, gracias! ¿Y tú cómo estás? Estoy aquí para escucharte."},
            
            # Crecimiento personal
            {"text": "crear tarea", "intent": "create_task", "response": "¡Me encanta tu iniciativa! Cada paso que das hacia el crecimiento personal es valioso. ¿Qué te gustaría explorar en tu viaje de autoconocimiento hoy?"},
            
            # Estados emocionales
            {"text": "me siento mal", "intent": "emotional_support", "response": "Entiendo que te sientes mal. Es normal tener días difíciles. ¿Puedes contarme más sobre lo que te está pasando? Estoy aquí para escucharte y apoyarte."},
            {"text": "estoy mal", "intent": "emotional_support", "response": "Entiendo que no te sientes bien. ¿Qué te está causando esta sensación? A veces hablar sobre ello puede ayudar."},
            {"text": "no me siento bien", "intent": "emotional_support", "response": "Es válido no sentirse bien. ¿Puedes contarme más sobre cómo te sientes? Estoy aquí para escucharte."},
            {"text": "me siento triste", "intent": "emotional_support", "response": "La tristeza es una emoción válida y natural. ¿Qué te está causando esta tristeza? A veces hablar sobre ello puede ayudar a procesar mejor los sentimientos."},
            {"text": "estoy deprimido", "intent": "emotional_support", "response": "La tristeza profunda es una emoción muy real y válida. ¿Has notado si hay algo específico que te está causando estos sentimientos? Es importante ser amable contigo mismo durante estos momentos."},
            {"text": "me siento ansioso", "intent": "emotional_support", "response": "Entiendo que te sientes ansioso. La ansiedad es una respuesta natural del cuerpo. ¿Puedes contarme más sobre lo que te está causando esta preocupación? A veces hablar sobre ello puede ayudar a reducir la intensidad."},
            {"text": "me siento bien", "intent": "positive_mood", "response": "¡Me alegra mucho que te sientas bien! Es genial cuando tenemos días positivos. ¿Qué te ha ayudado a sentirte así? Aprovecha esta energía positiva."},
            {"text": "estoy triste", "intent": "emotional_support", "response": "La tristeza es una emoción válida y natural. ¿Qué te está causando esta tristeza? A veces hablar sobre ello puede ayudar a procesar mejor los sentimientos."},
            {"text": "me siento perdido", "intent": "emotional_support", "response": "Sentirse perdido es parte del crecimiento personal. Es normal no tener todas las respuestas. ¿En qué área de tu vida te sientes más confundido? Juntos podemos explorar opciones."},
            {"text": "no tengo motivación", "intent": "emotional_support", "response": "La falta de motivación es algo que todos experimentamos. ¿Qué te gustaría lograr pero te cuesta empezar? A veces empezar con algo pequeño puede generar el impulso que necesitas."},
            {"text": "nueva tarea", "intent": "create_task", "response": "¡Excelente decisión! 🌟 Tu voluntad de crecer es admirable. ¿Qué aspecto de tu desarrollo personal te gustaría trabajar?"},
            {"text": "agregar tarea", "intent": "create_task", "response": "¡Perfecto! 💫 Tu deseo de mejorar es el primer paso hacia la transformación. ¿Qué te gustaría descubrir sobre ti mismo hoy?"},
            {"text": "tarea nueva", "intent": "create_task", "response": "¡Me encanta tu energía! 🌟 ¿Qué área de tu crecimiento personal te gustaría explorar?"},
            
            # Transformación personal
            {"text": "crear habito", "intent": "create_habit", "response": "¡Los cambios son tu superpoder! 🔥 Cada pequeño paso hacia el crecimiento personal es valioso. ¿Qué aspecto de tu desarrollo te gustaría explorar?"},
            {"text": "nuevo habito", "intent": "create_habit", "response": "¡Genial! 🌱 Tu voluntad de transformarte es admirable. ¿Qué área de tu crecimiento personal te gustaría trabajar?"},
            {"text": "establecer habito", "intent": "create_habit", "response": "¡Excelente! ⭐ Tu deseo de evolucionar es el primer paso hacia la transformación. ¿Qué te gustaría descubrir sobre tu potencial?"},
            {"text": "habito nuevo", "intent": "create_habit", "response": "¡Perfecto! 💫 ¿Qué aspecto de tu desarrollo personal te gustaría potenciar?"},
            
            # Reflexión personal
            {"text": "ver tareas", "intent": "view_tasks", "response": "¡Perfecto! 📋 Reflexionar sobre tu crecimiento es una excelente práctica de autoconciencia. ¿Qué aspecto de tu desarrollo personal te hace sentir más orgulloso?"},
            {"text": "mis tareas", "intent": "view_tasks", "response": "¡Genial idea! 🎯 Revisar tu evolución te ayuda a mantener la paz interior. ¿Cuál ha sido tu mayor logro de crecimiento reciente?"},
            {"text": "lista tareas", "intent": "view_tasks", "response": "¡Excelente! 📝 Reflexionar sobre tu progreso es una práctica de amor propio. ¿Qué aspecto de tu desarrollo te ha dado más satisfacción?"},
            {"text": "tareas existentes", "intent": "view_tasks", "response": "¡Perfecto! 🌟 ¿Qué área de tu crecimiento personal te gustaría celebrar hoy?"},
            
            # Evolución personal
            {"text": "ver habitos", "intent": "view_habits", "response": "¡Maravilloso! 🔄 Reflexionar sobre tu crecimiento es una práctica de autoconciencia profunda. ¿Qué aspecto de tu desarrollo te ha transformado más?"},
            {"text": "mis habitos", "intent": "view_habits", "response": "¡Perfecto! 🌱 Tu evolución personal es tu mejor inversión. ¿Qué área de tu crecimiento te ha dado más energía?"},
            {"text": "lista habitos", "intent": "view_habits", "response": "¡Genial! ⭐ Reflexionar sobre tu progreso te ayuda a mantener la motivación interior. ¿Qué aspecto de tu desarrollo te ha hecho más fuerte?"},
            {"text": "habitos existentes", "intent": "view_habits", "response": "¡Excelente! 💫 ¿Qué área de tu crecimiento personal te gustaría explorar más profundamente?"},
            
            # Consejos psicológicos
            {"text": "consejos", "intent": "productivity_tips", "response": "Aquí tienes algunos consejos que pueden ayudarte:\n\n• Sé amable contigo mismo en el proceso\n• Vive cada momento con consciencia plena\n• Reconoce las cosas buenas en tu vida\n• Protege tu energía y tu paz mental\n• Celebra cada paso en tu viaje\n\n¿Cuál de estos consejos te parece más útil?"},
            {"text": "productividad", "intent": "productivity_tips", "response": "Aquí tienes estrategias que pueden ayudarte:\n\n• Meditación matutina para conectar contigo mismo\n• Diario de gratitud para recordar lo bueno\n• Rutinas que nutran tu bienestar\n• Descansos conscientes para recargar energía\n• Celebración de tus logros diarios\n\n¿Qué estrategia te gustaría explorar?"},
            {"text": "mejorar productividad", "intent": "productivity_tips", "response": "Aquí tienes herramientas que pueden ayudarte:\n\n• Encuentra tu momento de paz diario\n• Respiración consciente para calmar la mente\n• Aprende a decir no cuando sea necesario\n• Suelta lo que ya no te sirve\n• Mantén un espacio que te haga sentir bien\n\n¿Cuál de estas herramientas te llama más la atención?"},
            
            # Análisis y estadísticas
            {"text": "estadisticas", "intent": "analytics", "response": "¡Excelente! Reflexionar sobre tu progreso es una forma de autoconciencia. ¿Qué aspecto de tu crecimiento personal te gustaría explorar más profundamente?"},
            {"text": "analytics", "intent": "analytics", "response": "¡Perfecto! Tu evolución cuenta una historia de transformación. ¿Qué área de tu desarrollo personal te gustaría potenciar?"},
            {"text": "progreso", "intent": "analytics", "response": "¡Genial! La reflexión es tu brújula hacia el autoconocimiento. ¿Qué área de tu vida quieres iluminar con mayor claridad?"},
            {"text": "ver progreso", "intent": "analytics", "response": "¡Excelente! Reflexionar sobre tu crecimiento es una práctica de amor propio. ¿Qué aspecto de tu desarrollo te gustaría celebrar?"},
            
            # Ayuda general
            {"text": "ayuda", "intent": "help", "response": "¡Estoy aquí para ti! 🌟 Puedo ayudarte con:\n\n• **Soporte emocional** y bienestar mental\n• **Motivación diaria** y energía positiva\n• **Desarrollo personal** y crecimiento interior\n• **Superación de obstáculos** y resiliencia\n• **Descubrimiento de tu potencial** ilimitado\n• **Consejos de vida** y sabiduría práctica\n\n¿En qué área te gustaría que te apoye hoy?"},
            {"text": "que puedes hacer", "intent": "help", "response": "¡Tu bienestar es mi prioridad! ✨ Puedo ayudarte con:\n\n• **Acompañamiento emocional** y estar presente en tu proceso\n• **Motivación interior** y encontrar tu fuego personal\n• **Crecimiento espiritual** y desarrollo de tu ser interior\n• **Superación personal** y transformar obstáculos en oportunidades\n• **Autoconocimiento** y descubrir tu verdadera esencia\n• **Soporte psicológico** y estar aquí para ti\n\n¿Qué aspecto de tu vida quieres explorar?"},
            {"text": "funciones", "intent": "help", "response": "¡Tu evolución es mi propósito! 💫 Estoy aquí para:\n\n• **Escucharte profundamente** y validar tu experiencia\n• **Inspirar tu crecimiento** y encontrar tu motivación interior\n• **Transformar tu perspectiva** y ver oportunidades en los desafíos\n• **Fortalecer tu espíritu** y desarrollar resiliencia mental\n• **Iluminar tu camino** y descubrir tu propósito\n• **Acompañarte emocionalmente** y estar presente en tu viaje\n\n¿Qué área de tu vida quieres iluminar hoy?"},
            
            # Despedidas
            {"text": "adiós", "intent": "goodbye", "response": "¡Que tengas un día increíble! 🌟 Recuerda que eres más fuerte de lo que crees y más capaz de lo que imaginas. ¡Nos vemos pronto! ✨"},
            {"text": "chao", "intent": "goodbye", "response": "¡Hasta la próxima! 💫 Que tu energía positiva te guíe hacia el éxito. ¡Eres increíble! 🌟"},
            {"text": "hasta luego", "intent": "goodbye", "response": "¡Que tengas un día maravilloso! 🌈 Tu potencial es ilimitado y tu futuro es brillante. ¡Nos vemos en tu próximo logro! 🚀"},
            {"text": "gracias", "intent": "goodbye", "response": "¡De nada! Estoy aquí para acompañarte siempre que lo necesites. ¡Tu crecimiento me inspira! 💫"},
        ]
    
    def _initialize_model(self):
        """Inicializar el modelo de TensorFlow"""
        try:
            # Preparar datos de entrenamiento
            texts = [item["text"] for item in self.training_data]
            intents = [item["intent"] for item in self.training_data]
            
            # Vectorizar texto
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            X = self.vectorizer.fit_transform(texts)
            
            # Codificar etiquetas
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(intents)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Convertir a formato TensorFlow
            X_train_dense = X_train.toarray()
            X_test_dense = X_test.toarray()
            
            # Crear modelo de red neuronal
            self.model = tf.keras.Sequential([
                tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train_dense.shape[1],)),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(len(self.label_encoder.classes_), activation='softmax')
            ])
            
            # Compilar modelo
            self.model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Entrenar modelo
            self.model.fit(
                X_train_dense, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test_dense, y_test),
                verbose=0
            )
            
            # Guardar modelo
            self._save_model()
            
            logger.info("✅ Modelo de TensorFlow entrenado y guardado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando modelo: {e}")
            # Fallback a modelo simple
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Crear modelo de respaldo simple"""
        logger.info("🔄 Creando modelo de respaldo...")
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
    
    def _save_model(self):
        """Guardar modelo entrenado"""
        try:
            if not os.path.exists(self.model_path):
                os.makedirs(self.model_path)
            
            self.model.save(self.model_path)
            
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            with open(self.label_encoder_path, 'wb') as f:
                pickle.dump(self.label_encoder, f)
                
            logger.info("✅ Modelo guardado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error guardando modelo: {e}")
    
    def _load_model(self):
        """Cargar modelo guardado"""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                    
                logger.info("✅ Modelo cargado exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            return False
    
    def _predict_intent(self, text: str) -> Dict[str, Any]:
        """Predecir intención usando el modelo de TensorFlow"""
        try:
            if self.model is None or self.vectorizer is None or self.label_encoder is None:
                return self._fallback_intent_prediction(text)
            
            # Vectorizar texto
            text_vectorized = self.vectorizer.transform([text])
            text_dense = text_vectorized.toarray()
            
            # Predecir
            predictions = self.model.predict(text_dense, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            # Decodificar intención
            intent = self.label_encoder.inverse_transform([predicted_class])[0]
            
            return {
                "intent": intent,
                "confidence": confidence,
                "predictions": predictions[0].tolist()
            }
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return self._fallback_intent_prediction(text)
    
    def _fallback_intent_prediction(self, text: str) -> Dict[str, Any]:
        """Predicción de respaldo usando reglas simples"""
        text_lower = text.lower()
        
        # Reglas simples para intenciones
        if any(word in text_lower for word in ['hola', 'buenos', 'buenas', 'como estas']):
            return {"intent": "greeting", "confidence": 0.8, "predictions": []}
        elif any(word in text_lower for word in ['tarea', 'crear', 'nueva', 'agregar']):
            return {"intent": "create_task", "confidence": 0.7, "predictions": []}
        elif any(word in text_lower for word in ['habito', 'establecer', 'nuevo']):
            return {"intent": "create_habit", "confidence": 0.7, "predictions": []}
        elif any(word in text_lower for word in ['ver', 'mis', 'lista', 'existentes']):
            if 'tarea' in text_lower:
                return {"intent": "view_tasks", "confidence": 0.8, "predictions": []}
            elif 'habito' in text_lower:
                return {"intent": "view_habits", "confidence": 0.8, "predictions": []}
        elif any(word in text_lower for word in ['consejo', 'productividad', 'mejorar']):
            return {"intent": "productivity_tips", "confidence": 0.6, "predictions": []}
        elif any(word in text_lower for word in ['estadistica', 'analytics', 'progreso']):
            return {"intent": "analytics", "confidence": 0.7, "predictions": []}
        elif any(word in text_lower for word in ['ayuda', 'puedes', 'funciones']):
            return {"intent": "help", "confidence": 0.6, "predictions": []}
        elif any(word in text_lower for word in ['adiós', 'chao', 'gracias', 'hasta']):
            return {"intent": "goodbye", "confidence": 0.8, "predictions": []}
        else:
            return {"intent": "general", "confidence": 0.3, "predictions": []}
    
    def _generate_intelligent_response(self, intent: str, text: str, user_context: Dict = None) -> Dict[str, Any]:
        """Generar respuesta inteligente basada en el contexto y la intención"""
        
        # Obtener contexto de conversación
        conversation_context = self._get_conversation_context()
        time_context = self._get_time_context()
        
        # Respuestas motivacionales según intención
        base_responses = {
            "greeting": [
                "¡Hola! ¿Cómo te sientes hoy? Estoy aquí para escucharte y apoyarte en tu viaje de crecimiento personal. 🌟",
                "¡Hola! Espero que tengas un día maravilloso. ¿Cómo va tu energía hoy? Estoy aquí para acompañarte. ✨",
                "¡Hola! ¿Cómo va tu día? Cuéntame qué pasa por tu mente y juntos encontraremos la luz en tu camino. 💪"
            ],
            "create_task": [
                "¡Me encanta tu iniciativa! 🎯 Cada paso que das hacia el crecimiento personal es valioso. ¿Qué te gustaría explorar en tu viaje de autoconocimiento hoy?",
                "¡Excelente decisión! 🌟 Tu voluntad de crecer es admirable. ¿Qué aspecto de tu desarrollo personal te gustaría trabajar?",
                "¡Perfecto! 💫 Tu deseo de mejorar es el primer paso hacia la transformación. ¿Qué te gustaría descubrir sobre ti mismo hoy?"
            ],
            "create_habit": [
                "¡Los cambios son tu superpoder! 🔥 Cada pequeño paso hacia el crecimiento personal es valioso. ¿Qué aspecto de tu desarrollo te gustaría explorar?",
                "¡Genial! 🌱 Tu voluntad de transformarte es admirable. ¿Qué área de tu crecimiento personal te gustaría trabajar?",
                "¡Excelente! ⭐ Tu deseo de evolucionar es el primer paso hacia la transformación. ¿Qué te gustaría descubrir sobre tu potencial?"
            ],
            "view_tasks": [
                "¡Perfecto! 📋 Reflexionar sobre tu crecimiento es una excelente práctica de autoconciencia. ¿Qué aspecto de tu desarrollo personal te hace sentir más orgulloso?",
                "¡Genial idea! 🎯 Revisar tu evolución te ayuda a mantener la claridad mental. ¿Cuál ha sido tu mayor logro de crecimiento reciente?",
                "¡Excelente! 📝 Reflexionar sobre tu progreso es una práctica de amor propio. ¿Qué aspecto de tu desarrollo te ha dado más satisfacción?"
            ],
            "view_habits": [
                "¡Maravilloso! 🔄 Reflexionar sobre tu crecimiento es una práctica de autoconciencia profunda. ¿Qué aspecto de tu desarrollo te ha transformado más?",
                "¡Perfecto! 🌱 Tu evolución personal es tu mejor inversión. ¿Qué área de tu crecimiento te ha dado más energía?",
                "¡Genial! ⭐ Reflexionar sobre tu progreso te ayuda a mantener la motivación interior. ¿Qué aspecto de tu desarrollo te ha hecho más fuerte?"
            ],
            "productivity_tips": [
                "¡Me encanta que quieras crecer! 🌟 Aquí tienes consejos que transformarán tu perspectiva:\n\n• **Autocompasión**: Sé amable contigo mismo en el proceso\n• **Presencia mental**: Vive cada momento con consciencia plena\n• **Gratitud diaria**: Reconoce las bendiciones en tu vida\n• **Límites saludables**: Protege tu energía y tu paz mental\n• **Celebración interior**: Honra cada paso en tu viaje\n\n¿Cuál de estos consejos resuena más con tu corazón?",
                "¡Tu evolución me inspira! ✨ Aquí tienes estrategias para el alma:\n\n• **Meditación matutina**: Conecta con tu esencia interior\n• **Diario de gratitud**: Escribe lo que te hace sentir vivo\n• **Rutinas que nutren**: Construye hábitos que alimenten tu espíritu\n• **Descansos conscientes**: Recarga tu energía con amor propio\n• **Celebración del ser**: Cada día es una oportunidad de brillar\n\n¿Qué estrategia te gustaría explorar primero?",
                "¡Tu luz interior es infinita! 💫 Aquí tienes herramientas para el alma:\n\n• **Momento de paz**: Encuentra tu espacio sagrado interior\n• **Respiración consciente**: Conecta con tu esencia en cada respiro\n• **Límites amorosos**: Aprende a decir no con compasión\n• **Liberación mental**: Suelta lo que ya no te sirve\n• **Organización del corazón**: Mantén un espacio que te eleve el espíritu\n\n¿Cuál de estas herramientas toca tu corazón?"
            ],
            "analytics": [
                "¡Excelente! 📊 Reflexionar sobre tu progreso es una forma de autoconciencia. ¿Qué aspecto de tu crecimiento personal te gustaría explorar más profundamente?",
                "¡Genial! 📈 Tu evolución cuenta una historia de transformación. ¿Qué área de tu desarrollo personal te gustaría potenciar?",
                "¡Perfecto! 📊 La reflexión es tu brújula hacia el autoconocimiento. ¿Qué área de tu vida quieres iluminar con mayor claridad?"
            ],
            "help": [
                "¡Estoy aquí para ti! 🌟 Puedo ayudarte con:\n\n• **Soporte emocional**: Escucharte y validar tus sentimientos\n• **Motivación diaria**: Encontrar tu energía interior\n• **Desarrollo personal**: Crecimiento y autoconocimiento\n• **Superación de obstáculos**: Resiliencia y fortaleza mental\n• **Descubrimiento de potencial**: Encontrar tu luz interior\n• **Bienestar mental**: Paz y equilibrio emocional\n• **Consejos de vida**: Sabiduría práctica para el día a día\n\n¿En qué área te gustaría que te apoye hoy?",
                "¡Tu bienestar es mi prioridad! ✨ Puedo ayudarte con:\n\n• **Acompañamiento emocional**: Estar presente en tu proceso\n• **Motivación interior**: Encontrar tu fuego personal\n• **Crecimiento espiritual**: Desarrollo de tu ser interior\n• **Superación personal**: Transformar obstáculos en oportunidades\n• **Autoconocimiento**: Descubrir tu verdadera esencia\n• **Soporte psicológico**: Estar aquí para ti\n• **Consejos prácticos**: Herramientas para la vida diaria\n\n¿Qué aspecto de tu vida quieres explorar?",
                "¡Tu evolución es mi propósito! 💫 Estoy aquí para:\n\n• **Escucharte profundamente**: Validar tu experiencia\n• **Inspirar tu crecimiento**: Encontrar tu motivación interior\n• **Transformar tu perspectiva**: Ver oportunidades en los desafíos\n• **Fortalecer tu espíritu**: Desarrollar resiliencia mental\n• **Iluminar tu camino**: Descubrir tu propósito\n• **Acompañarte emocionalmente**: Estar presente en tu viaje\n• **Guiarte con sabiduría**: Consejos para tu crecimiento\n\n¿Qué área de tu vida quieres iluminar hoy?"
            ],
            "goodbye": [
                "¡Que tengas un día increíble! 🌟 Recuerda que eres más fuerte de lo que crees y más capaz de lo que imaginas. ¡Nos vemos pronto! ✨",
                "¡Hasta la próxima! 💫 Que tu energía positiva te guíe hacia el éxito. ¡Eres increíble! 🌟",
                "¡Que tengas un día maravilloso! 🌈 Tu potencial es ilimitado y tu futuro es brillante. ¡Nos vemos en tu próximo logro! 🚀"
            ],
            "general": [
                "¡Me encanta escucharte! 🌟 Cuéntame más sobre cómo te sientes y juntos encontraremos la luz en tu camino. ¿Qué te gustaría explorar en tu corazón?",
                "¡Estoy aquí para ti! ✨ Cada palabra que compartes me ayuda a entender mejor cómo puedo acompañarte en tu viaje de crecimiento interior. ¿Qué te gustaría descubrir sobre ti mismo hoy?",
                "¡Tu bienestar es mi prioridad! 💫 Estoy aquí para escucharte, validar tus sentimientos y ayudarte a encontrar tu paz interior. ¿En qué área de tu ser te gustaría que te apoye?"
            ]
        }
        
        # Seleccionar respuesta base
        responses = base_responses.get(intent, base_responses["general"])
        base_response = random.choice(responses)
        
        # Personalizar respuesta según contexto
        personalized_response = self._personalize_response(base_response, conversation_context, time_context, user_context)
        
        # Generar sugerencias inteligentes
        suggestions = self._generate_smart_suggestions(intent, conversation_context)
        
        return {
            "response": personalized_response,
            "intent": intent,
            "confidence": 0.9,
            "sentiment": "positive",
            "sentiment_confidence": 0.8,
            "suggestions": suggestions,
            "entities": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_psychological_response(self, message: str, sentiment: str) -> str:
        """Sistema inteligente de respuesta psicológica simplificado y robusto"""
        try:
            logger.info(f"🧠 Analizando mensaje: '{message[:50]}...' con sentimiento: {sentiment}")
            
            # Análisis simple pero inteligente
            analysis = self._analyze_message_intelligently(message)
            
            # Generar respuesta basada en análisis
            response = self._generate_contextual_response(message, analysis, {}, sentiment)
            
            logger.info(f"🧠 Respuesta generada: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en _generate_psychological_response: {e}")
            # Respuesta de fallback
            return "Entiendo lo que dices. Es importante validar tus sentimientos y experiencias. ¿Puedes contarme más sobre cómo te sientes? Estoy aquí para escucharte y apoyarte en tu proceso."
    
    def _analyze_message_intelligently(self, message: str) -> Dict[str, Any]:
        """Análisis inteligente simplificado del mensaje"""
        message_lower = message.lower()
        
        # Análisis básico pero inteligente
        analysis = {
            'is_greeting': any(word in message_lower for word in ['hola', 'buenos', 'buenas', 'como estas']),
            'is_positive': any(word in message_lower for word in ['feliz', 'contento', 'bien', 'genial', 'excelente', 'perfecto', 'conseguí', 'logré', 'gané', 'trabajo', 'éxito', 'alegre']),
            'is_negative': any(word in message_lower for word in ['triste', 'mal', 'terrible', 'horrible', 'deprimido', 'ansioso', 'miedo', 'problema', 'difícil', 'no puedo', 'me siento mal']),
            'is_achievement': any(word in message_lower for word in ['conseguí', 'logré', 'gané', 'completé', 'terminé', 'alcanzé', 'obtuve', 'me dieron', 'me contrataron', 'pasé', 'aprobé']),
            'is_celebration': any(word in message_lower for word in ['me siento bien', 'estoy feliz', 'me alegra', 'estoy contento', 'es genial', 'es maravilloso', 'me encanta']),
            'is_struggle': any(word in message_lower for word in ['no puedo', 'no sé', 'me cuesta', 'es difícil', 'estoy perdido', 'no entiendo', 'tengo problemas', 'estoy confundido']),
            'is_gratitude': any(word in message_lower for word in ['gracias', 'agradecido', 'bendecido', 'afortunado', 'me siento bien']),
            'is_help_seeking': any(word in message_lower for word in ['ayuda', 'necesito', 'no sé qué hacer', 'qué hago', 'cómo', 'me siento perdido', 'no puedo más']),
            'has_question': '?' in message,
            'intensity': 1.0,
            'original_message': message
        }
        
        # Calcular intensidad
        intensity_words = ['muy', 'super', 'extremadamente', 'increíblemente', 'realmente', 'totalmente', 'completamente']
        for word in intensity_words:
            if word in message_lower:
                analysis['intensity'] *= 1.5
        
        # Determinar valencia emocional
        if analysis['is_positive'] or analysis['is_achievement'] or analysis['is_celebration']:
            analysis['valence'] = 'positive'
        elif analysis['is_negative'] or analysis['is_struggle']:
            analysis['valence'] = 'negative'
        else:
            analysis['valence'] = 'neutral'
        
        return analysis
    
    def _analyze_semantic_meaning(self, message: str) -> Dict[str, Any]:
        """Análisis semántico profundo del mensaje"""
        message_lower = message.lower()
        
        # Detectar patrones semánticos, no solo palabras
        semantic_patterns = {
            'achievement': self._detect_achievement_pattern(message),
            'struggle': self._detect_struggle_pattern(message),
            'celebration': self._detect_celebration_pattern(message),
            'seeking_help': self._detect_help_seeking_pattern(message),
            'sharing_experience': self._detect_experience_sharing_pattern(message),
            'reflection': self._detect_reflection_pattern(message),
            'planning': self._detect_planning_pattern(message),
            'gratitude': self._detect_gratitude_pattern(message)
        }
        
        return {
            'patterns': semantic_patterns,
            'main_topic': self._identify_main_topic(message),
            'temporal_context': self._analyze_temporal_context(message),
            'social_context': self._analyze_social_context(message)
        }
    
    def _detect_achievement_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de logro/éxito semánticamente"""
        patterns = {
            'has_achievement': False,
            'achievement_type': None,
            'confidence': 0.0
        }
        
        # Patrones semánticos de logro (no solo palabras específicas)
        achievement_indicators = [
            'conseguí', 'logré', 'gané', 'completé', 'terminé', 'alcanzé', 'obtuve',
            'me dieron', 'me contrataron', 'pasé', 'aprobé', 'superé', 'vencí',
            'lo hice', 'pude', 'salió bien', 'funcionó', 'resultó'
        ]
        
        # Análisis contextual de logro
        for indicator in achievement_indicators:
            if indicator in message.lower():
                patterns['has_achievement'] = True
                patterns['confidence'] += 0.3
                break
        
        # Detectar tipo de logro por contexto
        if 'trabajo' in message.lower() or 'empleo' in message.lower():
            patterns['achievement_type'] = 'work'
        elif 'estudio' in message.lower() or 'examen' in message.lower():
            patterns['achievement_type'] = 'academic'
        elif 'relación' in message.lower() or 'amor' in message.lower():
            patterns['achievement_type'] = 'relationship'
        else:
            patterns['achievement_type'] = 'general'
        
        return patterns
    
    def _detect_struggle_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de dificultad/lucha semánticamente"""
        patterns = {
            'has_struggle': False,
            'struggle_type': None,
            'intensity': 1.0
        }
        
        # Indicadores semánticos de dificultad
        struggle_indicators = [
            'no puedo', 'no sé', 'me cuesta', 'es difícil', 'estoy perdido',
            'no entiendo', 'me siento mal', 'tengo problemas', 'estoy confundido',
            'no funciona', 'no sale', 'me frustra', 'me agobia'
        ]
        
        for indicator in struggle_indicators:
            if indicator in message.lower():
                patterns['has_struggle'] = True
                break
        
        return patterns
    
    def _detect_celebration_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de celebración/positividad"""
        patterns = {
            'has_celebration': False,
            'celebration_type': None
        }
        
        # Indicadores semánticos de celebración
        celebration_indicators = [
            'me siento bien', 'estoy feliz', 'me alegra', 'estoy contento',
            'es genial', 'es maravilloso', 'me encanta', 'estoy emocionado'
        ]
        
        for indicator in celebration_indicators:
            if indicator in message.lower():
                patterns['has_celebration'] = True
                break
        
        return patterns
    
    def _detect_help_seeking_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de búsqueda de ayuda"""
        patterns = {
            'seeking_help': False,
            'help_type': None
        }
        
        help_indicators = [
            'ayuda', 'necesito', 'no sé qué hacer', 'qué hago', 'cómo',
            'me siento perdido', 'no puedo más', 'por favor'
        ]
        
        for indicator in help_indicators:
            if indicator in message.lower():
                patterns['seeking_help'] = True
                break
        
        return patterns
    
    def _detect_experience_sharing_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de compartir experiencia"""
        patterns = {
            'sharing_experience': False,
            'experience_type': None
        }
        
        # Detectar si está compartiendo una experiencia personal
        personal_indicators = [
            'me pasó', 'me ocurrió', 'me sucedió', 'me encontré',
            'descubrí', 'me di cuenta', 'experimenté', 'viví'
        ]
        
        for indicator in personal_indicators:
            if indicator in message.lower():
                patterns['sharing_experience'] = True
                break
        
        return patterns
    
    def _detect_reflection_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de reflexión"""
        patterns = {
            'is_reflection': False,
            'reflection_type': None
        }
        
        reflection_indicators = [
            'creo que', 'pienso que', 'me doy cuenta', 'reflexiono',
            'me pregunto', 'considero', 'evalúo', 'analizo'
        ]
        
        for indicator in reflection_indicators:
            if indicator in message.lower():
                patterns['is_reflection'] = True
                break
        
        return patterns
    
    def _detect_planning_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de planificación"""
        patterns = {
            'is_planning': False,
            'planning_type': None
        }
        
        planning_indicators = [
            'voy a', 'quiero', 'me gustaría', 'planeo', 'tengo planes',
            'espero', 'deseo', 'aspiro', 'busco'
        ]
        
        for indicator in planning_indicators:
            if indicator in message.lower():
                patterns['is_planning'] = True
                break
        
        return patterns
    
    def _detect_gratitude_pattern(self, message: str) -> Dict[str, Any]:
        """Detectar patrones de gratitud"""
        patterns = {
            'has_gratitude': False,
            'gratitude_type': None
        }
        
        gratitude_indicators = [
            'gracias', 'agradecido', 'bendecido', 'afortunado',
            'me siento bien', 'estoy agradecido', 'doy gracias'
        ]
        
        for indicator in gratitude_indicators:
            if indicator in message.lower():
                patterns['has_gratitude'] = True
                break
        
        return patterns
    
    def _identify_main_topic(self, message: str) -> str:
        """Identificar el tema principal del mensaje"""
        topics = {
            'work': ['trabajo', 'empleo', 'jefe', 'oficina', 'carrera', 'profesión'],
            'relationships': ['novio', 'novia', 'pareja', 'amigo', 'familia', 'relación'],
            'health': ['salud', 'enfermo', 'dolor', 'cuerpo', 'médico'],
            'education': ['estudio', 'universidad', 'colegio', 'examen', 'tarea'],
            'personal_growth': ['crecer', 'mejorar', 'desarrollar', 'aprender', 'cambiar'],
            'emotions': ['sentir', 'emoción', 'estado de ánimo', 'mood'],
            'daily_life': ['día', 'vida', 'rutina', 'actividades']
        }
        
        message_lower = message.lower()
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def _analyze_temporal_context(self, message: str) -> str:
        """Analizar contexto temporal"""
        temporal_indicators = {
            'past': ['ayer', 'antes', 'pasado', 'ocurrió', 'sucedió'],
            'present': ['hoy', 'ahora', 'actualmente', 'en este momento'],
            'future': ['mañana', 'después', 'pronto', 'planeo', 'voy a']
        }
        
        message_lower = message.lower()
        for time_frame, indicators in temporal_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return time_frame
        
        return 'present'
    
    def _analyze_social_context(self, message: str) -> str:
        """Analizar contexto social"""
        social_indicators = {
            'alone': ['solo', 'sola', 'sin nadie', 'por mi cuenta'],
            'with_others': ['con', 'junto', 'compañía', 'gente'],
            'seeking_connection': ['necesito', 'busco', 'quiero conectar']
        }
        
        message_lower = message.lower()
        for context, indicators in social_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return context
        
        return 'neutral'
    
    def _analyze_emotional_context(self, message: str, semantic_analysis: Dict) -> Dict[str, Any]:
        """Análisis contextual de emociones basado en significado"""
        valence = 'neutral'
        intensity = 1.0
        primary_emotion = 'neutral'
        
        # Analizar patrones semánticos para determinar valencia emocional
        if semantic_analysis['patterns']['achievement']['has_achievement']:
            valence = 'positive'
            intensity = 1.5
            primary_emotion = 'pride'
        elif semantic_analysis['patterns']['celebration']['has_celebration']:
            valence = 'positive'
            intensity = 1.3
            primary_emotion = 'happiness'
        elif semantic_analysis['patterns']['struggle']['has_struggle']:
            valence = 'negative'
            intensity = 1.4
            primary_emotion = 'frustration'
        elif semantic_analysis['patterns']['gratitude']['has_gratitude']:
            valence = 'positive'
            intensity = 1.2
            primary_emotion = 'gratitude'
        
        return {
            'valence': valence,
            'intensity': intensity,
            'primary_emotion': primary_emotion
        }
    
    def _analyze_communication_intent(self, message: str, semantic_analysis: Dict) -> str:
        """Analizar intención comunicativa"""
        if semantic_analysis['patterns']['help_seeking']['seeking_help']:
            return 'seeking_help'
        elif semantic_analysis['patterns']['experience_sharing']['sharing_experience']:
            return 'sharing_experience'
        elif semantic_analysis['patterns']['reflection']['is_reflection']:
            return 'reflection'
        elif semantic_analysis['patterns']['planning']['is_planning']:
            return 'planning'
        elif '?' in message:
            return 'question'
        else:
            return 'statement'
    
    def _analyze_urgency_context(self, message: str, semantic_analysis: Dict) -> Dict[str, Any]:
        """Analizar urgencia contextual"""
        urgency_indicators = ['ayuda', 'urgente', 'ahora', 'inmediatamente', 'por favor', 'necesito']
        is_urgent = any(indicator in message.lower() for indicator in urgency_indicators)
        
        return {
            'is_urgent': is_urgent,
            'urgency_level': 'high' if is_urgent else 'normal'
        }
    
    def _generate_contextual_response(self, message: str, analysis: Dict, context: Dict, sentiment: str) -> str:
        """Generar respuesta contextual basada en análisis inteligente simplificado"""
        
        # Manejo simple para saludos
        if analysis.get('is_greeting'):
            return "¡Hola! ¿Cómo te sientes hoy? Estoy aquí para escucharte y acompañarte en tu viaje de crecimiento personal."
        
        # Respuestas basadas en análisis inteligente
        if analysis.get('is_achievement'):
            return self._generate_achievement_response(analysis, context)
        
        if analysis.get('is_celebration'):
            return self._generate_celebration_response(analysis, context)
        
        if analysis.get('is_struggle'):
            return self._generate_struggle_response(analysis, context)
        
        if analysis.get('is_gratitude'):
            return self._generate_gratitude_response(analysis, context)
        
        if analysis.get('is_help_seeking'):
            return self._generate_help_response(analysis, context)
        
        if analysis.get('has_question'):
            return self._generate_question_response(analysis, context)
        
        # Respuestas basadas en valencia emocional
        if analysis.get('valence') == 'positive':
            return self._generate_positive_context_response(analysis, context)
        
        if analysis.get('valence') == 'negative':
            return self._generate_negative_context_response(analysis, context)
        
        # Respuesta contextual general inteligente
        return self._generate_intelligent_general_response(analysis, context)
    
    def _generate_achievement_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para logros/éxitos"""
        message_lower = analysis.get('original_message', '').lower()
        
        # Determinar tipo de logro por contexto
        if 'trabajo' in message_lower or 'empleo' in message_lower:
            achievement_type = 'work'
        elif 'estudio' in message_lower or 'examen' in message_lower:
            achievement_type = 'academic'
        else:
            achievement_type = 'general'
        
        responses = {
            'work': [
                "¡Felicidades por tu logro profesional! Es un momento importante que merece ser celebrado. ¿Cómo te sientes con respecto a este nuevo paso en tu carrera?",
                "¡Excelente trabajo! Los logros profesionales son el resultado de tu esfuerzo y dedicación. ¿Qué te ha enseñado este proceso?",
                "¡Qué gran logro laboral! Es valioso reconocer cuando las cosas salen bien. ¿Qué te gustaría hacer para celebrar este momento?"
            ],
            'academic': [
                "¡Felicidades por tu logro académico! El conocimiento es una inversión en ti mismo. ¿Cómo te sientes con respecto a lo que has aprendido?",
                "¡Excelente trabajo académico! Cada logro educativo te acerca más a tus metas. ¿Qué te ha enseñado este proceso?",
                "¡Qué gran logro en tus estudios! Es importante celebrar estos momentos de crecimiento. ¿Qué te gustaría hacer para reconocer este esfuerzo?"
            ],
            'general': [
                "¡Felicidades por tu logro! Es importante celebrar nuestros éxitos. ¿Cómo te sientes con respecto a lo que has conseguido?",
                "¡Excelente trabajo! Los logros son el resultado de tu esfuerzo y dedicación. ¿Qué te ha enseñado este proceso?",
                "¡Qué gran logro! Es valioso reconocer cuando las cosas salen bien. ¿Qué te gustaría hacer para celebrar este momento?"
            ]
        }
        
        return random.choice(responses.get(achievement_type, responses['general']))
    
    def _generate_celebration_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para celebraciones/positividad"""
        responses = [
            "¡Me alegra mucho que tengas algo que celebrar! Es genial cuando tenemos momentos positivos. ¿Qué te ha ayudado a sentirte así? Aprovecha esta energía positiva.",
            "¡Qué maravilloso que tengas algo que celebrar! La felicidad es un regalo que debemos valorar. ¿Qué te gustaría hacer para mantener esta sensación?",
            "¡Es fantástico que tengas algo que celebrar! La alegría nos conecta con nuestra mejor versión. ¿Qué te ha traído esta celebración? Disfruta cada momento."
        ]
        return random.choice(responses)
    
    def _generate_struggle_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para dificultades/luchas"""
        responses = [
            "Veo que estás pasando por un momento difícil. Es importante que sepas que no estás solo en esto. ¿Qué es lo que más te está afectando? A veces hablar sobre ello puede ayudar a que se sienta menos abrumador.",
            "Entiendo que estás enfrentando desafíos. Es valiente de tu parte reconocer cuando las cosas son difíciles. ¿Qué te gustaría hacer para cuidarte en este momento?",
            "Los momentos difíciles son parte del crecimiento, aunque no siempre lo parezca. ¿Qué crees que necesitas para poder avanzar? A veces pequeños pasos pueden hacer una gran diferencia."
        ]
        return random.choice(responses)
    
    def _generate_gratitude_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para gratitud"""
        responses = [
            "Es hermoso que sientas gratitud. La gratitud nos conecta con lo que realmente importa. ¿Qué te hace sentir más agradecido en este momento?",
            "La gratitud es una práctica que enriquece el alma. Es valioso que reconozcas las cosas buenas en tu vida. ¿Qué te gustaría hacer para expresar esta gratitud?",
            "Me alegra que sientas gratitud. Es una emoción que nos conecta con nuestra mejor versión. ¿Qué te ha ayudado a sentirte agradecido?"
        ]
        return random.choice(responses)
    
    def _generate_help_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para búsqueda de ayuda"""
        responses = [
            "Entiendo que necesitas ayuda. Es valiente de tu parte pedirla. ¿Qué es lo que más necesitas en este momento? Estoy aquí para escucharte y apoyarte.",
            "Veo que estás buscando ayuda. Es importante reconocer cuando necesitamos apoyo. ¿Qué te gustaría explorar o trabajar? Juntos podemos encontrar soluciones.",
            "Es completamente normal necesitar ayuda. Todos pasamos por momentos difíciles. ¿Qué te está causando más angustia? A veces el simple hecho de hablar puede traer claridad."
        ]
        return random.choice(responses)
    
    def _generate_question_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para preguntas"""
        responses = [
            "Es una excelente pregunta. ¿Qué te hace pensar en esto? A veces explorar nuestras propias preguntas nos lleva a respuestas interesantes.",
            "Me gusta tu curiosidad. ¿Qué te ha llevado a hacer esta pregunta? A veces el proceso de cuestionar es más valioso que la respuesta.",
            "Es una pregunta que merece reflexión. ¿Qué crees que te está motivando a buscar esta respuesta? A veces nuestras preguntas revelan nuestras necesidades más profundas."
        ]
        return random.choice(responses)
    
    def _generate_positive_context_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para contexto positivo"""
        responses = [
            "Me alegra que estés en un momento positivo. Es importante aprovechar estos momentos de bienestar. ¿Qué te ha ayudado a sentirte así?",
            "Es genial que estés experimentando emociones positivas. La positividad nos conecta con nuestra mejor versión. ¿Qué te gustaría hacer para mantener esta energía?",
            "Me encanta tu energía positiva. Es contagiosa y valiosa. ¿Qué te ha traído esta sensación de bienestar?"
        ]
        return random.choice(responses)
    
    def _generate_negative_context_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta para contexto negativo"""
        responses = [
            "Entiendo que estés pasando por un momento difícil. Es importante que sepas que tus sentimientos son válidos. ¿Qué te gustaría explorar sobre lo que estás experimentando?",
            "Veo que estás en un momento desafiante. Es valiente de tu parte compartir lo que sientes. ¿Qué necesitas más en este momento?",
            "Los momentos difíciles son parte del crecimiento, aunque no siempre lo parezca. ¿Qué te gustaría hacer para cuidarte? A veces el autocuidado puede hacer una gran diferencia."
        ]
        return random.choice(responses)
    
    def _generate_intelligent_general_response(self, analysis: Dict, context: Dict) -> str:
        """Respuesta general inteligente basada en análisis semántico"""
        responses = [
            "Gracias por compartir eso conmigo. Es valioso que puedas expresar lo que sientes. ¿Qué te gustaría explorar más sobre esta experiencia?",
            "Me siento honrado de que me compartas esto. Cada palabra que dices me ayuda a entender mejor cómo puedo acompañarte. ¿Qué es lo que más necesitas en este momento?",
            "Es importante que puedas expresar lo que sientes. Cada experiencia es única y valiosa. ¿Qué te gustaría trabajar o entender mejor?",
            "Gracias por tu honestidad. Es valioso que puedas ser auténtico sobre lo que experimentas. ¿Qué te gustaría explorar sobre esto?"
        ]
        return random.choice(responses)
    
    def _get_conversation_context(self) -> Dict[str, Any]:
        """Obtener contexto de la conversación"""
        if len(self.conversation_history) < 2:
            return {"recent_topics": [], "recent_intents": [], "user_mood": "neutral", "interaction_count": 0}
        
        recent_messages = self.conversation_history[-5:]  # Últimos 5 mensajes
        topics = []
        intents = []
        
        for msg in recent_messages:
            if msg.get("intent"):
                topics.append(msg["intent"])
                intents.append(msg["intent"])
        
        return {
            "recent_topics": topics,
            "recent_intents": intents,
            "user_mood": self._analyze_user_mood(recent_messages),
            "interaction_count": len(self.conversation_history)
        }
    
    def _get_time_context(self) -> Dict[str, Any]:
        """Obtener contexto temporal"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            time_period = "morning"
            greeting = "¡Buenos días!"
        elif 12 <= hour < 18:
            time_period = "afternoon"
            greeting = "¡Buenas tardes!"
        else:
            time_period = "evening"
            greeting = "¡Buenas noches!"
        
        return {
            "time_period": time_period,
            "greeting": greeting,
            "hour": hour,
            "is_weekend": now.weekday() >= 5
        }
    
    def _analyze_user_mood(self, messages: List[Dict]) -> str:
        """Analizar el estado de ánimo del usuario de forma psicológica"""
        positive_words = ["genial", "excelente", "perfecto", "gracias", "ayuda", "bien", "feliz", "contento", "emocionado", "motivado", "energía", "increíble", "maravilloso", "fantástico", "brillante", "exitoso", "logrado", "conseguido", "alcanzado", "superado", "conseguí", "logré", "gané", "trabajo", "éxito", "alegre", "orgulloso", "satisfecho"]
        negative_words = ["mal", "problema", "difícil", "no puedo", "frustrado", "cansado", "estresado", "ansioso", "preocupado", "triste", "deprimido", "agotado", "desmotivado", "perdido", "confundido", "abrumado", "desanimado", "desesperado", "solo", "solitario"]
        neutral_words = ["normal", "regular", "ok", "bien", "tranquilo", "calmado", "equilibrado", "estable", "centrado", "balanceado"]
        
        text = " ".join([msg.get("text", "").lower() for msg in messages])
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        neutral_count = sum(1 for word in neutral_words if word in text)
        
        if positive_count > negative_count and positive_count > neutral_count:
            return "positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            return "negative"
        else:
            return "neutral"
    
    def _personalize_response(self, base_response: str, conversation_context: Dict, time_context: Dict, user_context: Dict = None) -> str:
        """Personalizar respuesta según contexto"""
        personalized = base_response
        
        # Agregar saludo temporal si es apropiado
        if "greeting" in conversation_context.get("recent_topics", []) and time_context["greeting"] not in personalized:
            personalized = f"{time_context['greeting']} {personalized}"
        
        # Personalizar según el estado de ánimo
        if conversation_context.get("user_mood") == "positive":
            personalized += "\n\n¡Me encanta tu energía positiva! Vamos a aprovecharla al máximo."
        elif conversation_context.get("user_mood") == "negative":
            personalized += "\n\nEntiendo que puede ser desafiante. Estoy aquí para ayudarte a superarlo."
        
        # Contexto de tiempo (eliminado para respuestas más limpias)
        pass
        
        return personalized
    
    def _generate_smart_suggestions(self, intent: str, conversation_context: Dict) -> List[str]:
        """Generar sugerencias psicológicas y motivacionales"""
        suggestions_map = {
            "greeting": ["Me siento bien", "Me siento mal", "Necesito motivación"],
            "create_task": ["Me siento abrumado", "No tengo motivación", "Necesito apoyo"],
            "create_habit": ["Me cuesta ser consistente", "Me siento estancado", "Necesito cambiar"],
            "view_tasks": ["Me siento abrumado", "No sé por dónde empezar", "Me falta motivación"],
            "view_habits": ["Me cuesta ser consistente", "Me siento frustrado", "No veo progreso"],
            "productivity_tips": ["Me siento bloqueado", "Necesito inspiración", "Me falta confianza"],
            "analytics": ["Me siento estancado", "No veo progreso", "Necesito motivación"],
            "help": ["Me siento perdido", "Cuéntame más", "Necesito apoyo"],
            "goodbye": ["Gracias por escucharme", "Hasta la próxima", "Que tengas un día increíble"],
            "general": ["Me siento bien", "Me siento mal", "Necesito motivación"]
        }
        
        return suggestions_map.get(intent, ["¿Cómo te sientes?", "Cuéntame más"])
    
    # Función de insights eliminada para respuestas más limpias
    
    def _should_create_task(self, text: str, conversation_context: Dict) -> bool:
        """Determinar si el usuario quiere crear una tarea"""
        text_lower = text.lower()
        
        # Palabras clave para creación de tareas
        task_keywords = ['tarea', 'crear', 'nueva', 'agregar', 'añadir', 'hacer', 'completar']
        
        # Verificar si el mensaje anterior fue sobre crear tarea
        recent_intents = conversation_context.get('recent_intents', [])
        was_creating_task = 'create_task' in recent_intents[-2:] if len(recent_intents) >= 2 else False
        
        # Si el mensaje anterior fue sobre crear tarea y este mensaje no es muy largo, probablemente es el nombre
        if was_creating_task and len(text.split()) <= 10 and not any(word in text_lower for word in ['no', 'cancelar', 'olvidar']):
            return True
        
        return False
    
    def _should_create_habit(self, text: str, conversation_context: Dict) -> bool:
        """Determinar si el usuario quiere crear un hábito"""
        text_lower = text.lower()
        
        # Palabras clave para creación de hábitos
        habit_keywords = ['habito', 'hábito', 'crear', 'nuevo', 'establecer', 'formar']
        
        # Verificar si el mensaje anterior fue sobre crear hábito
        recent_intents = conversation_context.get('recent_intents', [])
        was_creating_habit = 'create_habit' in recent_intents[-2:] if len(recent_intents) >= 2 else False
        
        # Si el mensaje anterior fue sobre crear hábito y este mensaje no es muy largo, probablemente es el nombre
        if was_creating_habit and len(text.split()) <= 10 and not any(word in text_lower for word in ['no', 'cancelar', 'olvidar']):
            return True
        
        return False
    
    def _handle_task_creation(self) -> Dict[str, Any]:
        """Manejar creación de tarea"""
        return {
            "response": "¡Perfecto! ¿Qué tarea te gustaría crear? Dime el nombre o descripción de la tarea que quieres agregar.",
            "intent": "task_creation_prompt",
            "confidence": 0.9,
            "sentiment": "positive",
            "sentiment_confidence": 0.8,
            "suggestions": ["Completar proyecto", "Estudiar para examen", "Hacer ejercicio"],
            "entities": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _handle_habit_creation(self) -> Dict[str, Any]:
        """Manejar creación de hábito"""
        return {
            "response": "¡Excelente! ¿Qué hábito te gustaría establecer? Dime el nombre del hábito que quieres crear.",
            "intent": "habit_creation_prompt",
            "confidence": 0.9,
            "sentiment": "positive",
            "sentiment_confidence": 0.8,
            "suggestions": ["Meditar diariamente", "Leer 30 minutos", "Hacer ejercicio"],
            "entities": {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _handle_task_creation_response(self, task_name: str) -> Dict[str, Any]:
        """Manejar respuesta con nombre de tarea"""
        # Generar datos de tarea
        priority = random.choice(["low", "medium", "high"])
        status = "pending"
        
        task_data = {
            "title": task_name,
            "description": task_name,
            "priority": priority,
            "status": status
        }
        
        return {
            "response": f"¡Perfecto! He creado la tarea: **{task_name}**\n\n📝 **Descripción:** {task_name}\n🎯 **Prioridad:** {priority}\n📊 **Estado:** {status}\n\n✅ **Tarea creada exitosamente en tu base de datos**\n\n💡 **Consejo:** Divide las tareas grandes en pasos pequeños para mayor éxito.",
            "intent": "task_creation_complete",
            "confidence": 0.95,
            "sentiment": "positive",
            "sentiment_confidence": 0.9,
            "suggestions": ["Ver mis tareas", "Crear nueva tarea"],
            "entities": {"task_name": task_name, "priority": priority},
            "timestamp": datetime.utcnow().isoformat(),
            "task_created": task_data
        }
    
    def _handle_habit_creation_response(self, habit_name: str) -> Dict[str, Any]:
        """Manejar respuesta con nombre de hábito"""
        # Generar datos de hábito
        frequency = random.choice(["daily", "weekly", "monthly"])
        time_of_day = random.choice(["morning", "afternoon", "evening", "flexible"])
        
        habit_data = {
            "name": habit_name,
            "description": habit_name,
            "frequency": frequency,
            "time_of_day": time_of_day
        }
        
        return {
            "response": f"¡Perfecto! He creado el hábito: **{habit_name}**\n\n📝 **Descripción:** {habit_name}\n🔄 **Frecuencia:** {frequency}\n⏰ **Momento:** {time_of_day}\n\n✅ **Hábito creado exitosamente en tu base de datos**\n\n💡 **Consejo:** Los hábitos se forman en 21 días. ¡Mantén la consistencia!",
            "intent": "habit_creation_complete",
            "confidence": 0.95,
            "sentiment": "positive",
            "sentiment_confidence": 0.9,
            "suggestions": ["Ver mis hábitos", "Crear nuevo hábito"],
            "entities": {"habit_name": habit_name, "frequency": frequency},
            "timestamp": datetime.utcnow().isoformat(),
            "habit_created": habit_data
        }
    
    def process_message(self, message: str, user_id: str = None, user_context: Dict = None) -> Dict[str, Any]:
        """Procesar mensaje usando TensorFlow ML"""
        try:
            # Agregar mensaje al historial
            self.conversation_history.append({
                "text": message,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id
            })
            
            # Mantener solo los últimos 20 mensajes
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Obtener contexto
            conversation_context = self._get_conversation_context()
            
            # Verificar si es respuesta a creación de tarea/hábito
            if self._should_create_task(message, conversation_context):
                return self._handle_task_creation_response(message)
            
            if self._should_create_habit(message, conversation_context):
                return self._handle_habit_creation_response(message)
            
            # Predecir intención usando TensorFlow
            prediction = self._predict_intent(message)
            intent = prediction["intent"]
            confidence = prediction["confidence"]
            
            # Manejar intenciones especiales
            if intent == "create_task":
                return self._handle_task_creation()
            
            if intent == "create_habit":
                return self._handle_habit_creation()
            
            # Generar respuesta inteligente
            if intent == "general":
                # Usar respuesta inteligente para temas psicológicos
                intelligent_response = self._generate_psychological_response(message, "neutral")
                response = {
                    "response": intelligent_response,
                    "intent": intent,
                    "confidence": confidence,
                    "sentiment": "neutral",
                    "sentiment_confidence": 0.5,
                    "suggestions": ["Me siento bien", "Me siento mal", "Necesito motivación"],
                    "entities": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif intent == "emotional_support":
                # Usar respuesta específica para apoyo emocional
                intelligent_response = self._generate_psychological_response(message, "negative")
                logger.info(f"🧠 Respuesta psicológica generada: {intelligent_response[:100]}...")
                response = {
                    "response": intelligent_response,
                    "intent": intent,
                    "confidence": confidence,
                    "sentiment": "negative",
                    "sentiment_confidence": 0.7,
                    "suggestions": ["Me siento mejor", "Necesito ayuda", "Quiero hablar más"],
                    "entities": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Para todas las demás intenciones, usar respuesta inteligente
                intelligent_response = self._generate_psychological_response(message, "neutral")
                response = {
                    "response": intelligent_response,
                    "intent": intent,
                    "confidence": confidence,
                    "sentiment": "neutral",
                    "sentiment_confidence": 0.5,
                    "suggestions": ["Me siento bien", "Me siento mal", "Necesito motivación"],
                    "entities": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                "text": response["response"],
                "intent": intent,
                "timestamp": datetime.utcnow().isoformat(),
                "is_ai": True
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            return {
                "response": "¡Ups! Tuve un pequeño problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?",
                "intent": "error",
                "confidence": 0.0,
                "sentiment": "neutral",
                "sentiment_confidence": 0.0,
                "suggestions": ["Crear una tarea", "Establecer un hábito", "Ver todas mis tareas"],
                "entities": {},
                "timestamp": datetime.utcnow().isoformat()
            }
