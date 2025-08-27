#!/usr/bin/env python3
"""
Servicio principal de IA - Integración con TensorFlow ML
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .tensorflow_ai_service import TensorFlowAIService

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Inicializar servicio de IA con TensorFlow"""
        try:
            logger.info("🧠 Inicializando servicio de IA con TensorFlow...")
            self.tensorflow_ai = TensorFlowAIService()
            logger.info("✅ Servicio de IA con TensorFlow inicializado exitosamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio de IA: {e}")
            self.tensorflow_ai = None
    
    def process_message(self, message: str, user_id: str = None, user_context: Dict = None) -> Dict[str, Any]:
        """Procesar mensaje usando TensorFlow ML"""
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
        
        return {
            "response": "¡Hola! Soy tu psicólogo motivacional personal. 🌟 Estoy aquí para escucharte, apoyarte y ayudarte a descubrir tu mejor versión.\n\nPuedo ayudarte con:\n\n• **Soporte emocional** y bienestar mental\n• **Motivación diaria** y energía positiva\n• **Desarrollo personal** y crecimiento interior\n• **Superación de obstáculos** y resiliencia\n• **Descubrimiento de tu potencial** ilimitado\n• **Consejos de vida** y sabiduría práctica\n• **Acompañamiento psicológico** en tu viaje\n\n¿Cómo te sientes hoy? Cuéntame qué pasa por tu mente.",
            "intent": "greeting",
            "confidence": 0.5,
            "sentiment": "positive",
            "sentiment_confidence": 0.6,
            "suggestions": ["Me siento bien", "Me siento mal", "Necesito motivación"],
            "entities": {},
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
