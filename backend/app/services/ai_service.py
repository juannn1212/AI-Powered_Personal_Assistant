#!/usr/bin/env python3
"""
Servicio principal de IA - Integración con TensorFlow ML
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from . import emotional_support

try:  # TensorFlow es opcional: la capa de seguridad funciona sin él
    from .tensorflow_ai_service import TensorFlowAIService
except Exception as _e:  # pragma: no cover
    TensorFlowAIService = None
    logging.getLogger(__name__).warning(f"TensorFlow no disponible: {_e}")

logger = logging.getLogger(__name__)

GREETING_TEXT = (
    "¡Hola! Soy tu asistente de bienestar y productividad. Puedo ayudarte a organizar tareas y hábitos, "
    "y también acompañarte cuando te sientas estresado/a o abrumado/a.\n\n"
    "Soy un asistente de IA, no un profesional de salud mental ni un servicio de emergencias.\n\n"
    "¿Cómo te sientes hoy?"
)

class AIService:
    def __init__(self):
        """Inicializar servicio de IA con TensorFlow"""
        try:
            logger.info("🧠 Inicializando servicio de IA con TensorFlow...")
            if TensorFlowAIService is None:
                raise RuntimeError("TensorFlow no está instalado")
            self.tensorflow_ai = TensorFlowAIService()
            logger.info("✅ Servicio de IA con TensorFlow inicializado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio de IA: {e}")
            self.tensorflow_ai = None
    
    def process_message(self, message: str, user_id: str = None, user_context: Dict = None) -> Dict[str, Any]:
        """Procesar mensaje usando TensorFlow ML"""
        # Seguridad primero, también cuando el modelo no está disponible o falla
        crisis = emotional_support.check_crisis(message)
        if crisis:
            return emotional_support.to_response(crisis)
        try:
            if self.tensorflow_ai is None:
                logger.error("❌ Servicio de TensorFlow no disponible")
                return self._generate_fallback_response(message)
            
            # Procesar mensaje con TensorFlow
            response = self.tensorflow_ai.process_message(message, user_id, user_context)
            
            logger.info(f"✅ Mensaje procesado con TensorFlow - Intención: {response.get('intent')}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje con TensorFlow: {e}")
            return self._generate_fallback_response(message)
    
    def _generate_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generar respuesta de respaldo si TensorFlow falla"""
        logger.warning("🔄 Usando respuesta de respaldo")

        support = emotional_support.analyze(message)
        if support:
            return emotional_support.to_response(support)

        return {
            "response": GREETING_TEXT,
            "intent": "greeting",
            "confidence": 0.5,
            "sentiment": "neutral",
            "sentiment_confidence": 0.5,
            "suggestions": ["Me siento mal", "Ver mis tareas", "Crear un hábito"],
            "entities": {},
            "emotion": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo de TensorFlow"""
        try:
            if self.tensorflow_ai and self.tensorflow_ai.model:
                return {
                    "model_type": "TensorFlow Neural Network",
                    "status": "active",
                    "features": [
                        "Intent Classification",
                        "Sentiment Analysis", 
                        "Context Awareness",
                        "Personalized Responses",
                        "Smart Suggestions",
                        "Task/Habit Creation"
                    ],
                    "training_data_size": len(self.tensorflow_ai.training_data),
                    "model_architecture": "Dense Neural Network (128-64-output)",
                    "last_updated": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "model_type": "Fallback Rule-based",
                    "status": "fallback",
                    "features": ["Basic Intent Recognition"],
                    "message": "TensorFlow model not available"
                }
        except Exception as e:
            logger.error(f"❌ Error obteniendo información del modelo: {e}")
            return {
                "model_type": "Error",
                "status": "error",
                "error": str(e)
            }
