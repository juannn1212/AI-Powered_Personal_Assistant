import openai
from typing import Dict, List, Optional, Tuple
import json
import logging
from app.config import settings
from app.services.ml_service import MLService

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.ml_service = MLService()
        
        # System prompts for different contexts
        self.system_prompts = {
            "general": """You are an AI-powered personal assistant designed to help users optimize their productivity and daily habits. 
            You should be helpful, friendly, and provide actionable advice. Always respond in Spanish unless the user asks otherwise.""",
            
            "task_management": """You are a task management assistant. Help users organize, prioritize, and track their tasks effectively. 
            Provide specific, actionable advice for task completion and time management.""",
            
            "habit_tracking": """You are a habit formation and tracking assistant. Help users build positive habits and break negative ones. 
            Provide motivation, accountability, and practical strategies for habit success.""",
            
            "productivity": """You are a productivity optimization assistant. Help users maximize their efficiency, focus, and time management. 
            Provide evidence-based strategies and personalized recommendations."""
        }
    
    async def process_message(self, message: str, user_context: Dict = None, intent: str = "general") -> Dict:
        """
        Process user message and generate AI response
        """
        try:
            # Analyze intent if not provided
            if not intent or intent == "general":
                intent = await self._analyze_intent(message)
            
            # Get appropriate system prompt
            system_prompt = self.system_prompts.get(intent, self.system_prompts["general"])
            
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(user_context)
            
            # Generate response using OpenAI
            response = await self._generate_response(
                message=message,
                system_prompt=system_prompt,
                context_prompt=context_prompt
            )
            
            # Analyze response sentiment and confidence
            sentiment = await self._analyze_sentiment(response)
            confidence = await self._calculate_confidence(message, response)
            
            return {
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "sentiment": sentiment,
                "suggestions": await self._generate_suggestions(intent, user_context)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?",
                "intent": "error",
                "confidence": 0.0,
                "sentiment": "neutral",
                "suggestions": []
            }
    
    async def _generate_response(self, message: str, system_prompt: str, context_prompt: str = "") -> str:
        """
        Generate response using OpenAI API
        """
        try:
            full_prompt = f"{system_prompt}\n\n{context_prompt}\n\nUsuario: {message}\n\nAsistente:"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context_prompt}\n\n{message}"}
                ],
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."
    
    async def _analyze_intent(self, message: str) -> str:
        """
        Analyze user intent using ML model
        """
        try:
            # Use ML service to classify intent
            intent = await self.ml_service.classify_intent(message)
            return intent
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return "general"
    
    async def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following text and respond with only one word: positive, negative, or neutral."},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            return sentiment if sentiment in ["positive", "negative", "neutral"] else "neutral"
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return "neutral"
    
    async def _calculate_confidence(self, message: str, response: str) -> float:
        """
        Calculate confidence score for the response
        """
        try:
            # Simple heuristic-based confidence calculation
            confidence = 0.8  # Base confidence
            
            # Adjust based on response length and quality
            if len(response) > 50:
                confidence += 0.1
            
            if "?" in message:  # Question detected
                confidence += 0.05
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _build_context_prompt(self, user_context: Dict = None) -> str:
        """
        Build context-aware prompt based on user data
        """
        if not user_context:
            return ""
        
        context_parts = []
        
        if user_context.get("recent_tasks"):
            context_parts.append(f"Tareas recientes: {', '.join(user_context['recent_tasks'])}")
        
        if user_context.get("habits"):
            context_parts.append(f"Hábitos activos: {', '.join(user_context['habits'])}")
        
        if user_context.get("productivity_score"):
            context_parts.append(f"Puntuación de productividad: {user_context['productivity_score']}/10")
        
        if user_context.get("mood"):
            context_parts.append(f"Estado de ánimo: {user_context['mood']}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def _generate_suggestions(self, intent: str, user_context: Dict = None) -> List[str]:
        """
        Generate personalized suggestions based on intent and context
        """
        suggestions = []
        
        if intent == "task_management":
            suggestions = [
                "¿Te gustaría que te ayude a priorizar tus tareas?",
                "¿Quieres que programe recordatorios para tus tareas pendientes?",
                "¿Necesitas ayuda para dividir una tarea compleja en pasos más pequeños?"
            ]
        elif intent == "habit_tracking":
            suggestions = [
                "¿Quieres que te ayude a crear un nuevo hábito?",
                "¿Te gustaría revisar tu progreso en los hábitos actuales?",
                "¿Necesitas motivación para mantener tus hábitos?"
            ]
        elif intent == "productivity":
            suggestions = [
                "¿Quieres que analice tu patrón de productividad?",
                "¿Te gustaría recibir consejos para mejorar tu enfoque?",
                "¿Necesitas ayuda para optimizar tu rutina diaria?"
            ]
        else:
            suggestions = [
                "¿En qué puedo ayudarte hoy?",
                "¿Quieres que revise tus tareas pendientes?",
                "¿Te gustaría que analice tu productividad?"
            ]
        
        return suggestions
    
    async def generate_task_suggestions(self, user_tasks: List[Dict]) -> List[Dict]:
        """
        Generate AI-powered task suggestions
        """
        try:
            task_context = "\n".join([f"- {task['title']}: {task['description']}" for task in user_tasks])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Based on the user's tasks, suggest 3-5 new tasks that would complement their current workload. Return as JSON array with 'title' and 'description' fields."},
                    {"role": "user", "content": f"Current tasks:\n{task_context}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            suggestions = json.loads(suggestions_text)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating task suggestions: {e}")
            return []
    
    async def analyze_productivity_patterns(self, user_data: Dict) -> Dict:
        """
        Analyze user productivity patterns and provide insights
        """
        try:
            analysis_prompt = f"""
            Analyze the following user productivity data and provide insights:
            
            Tasks completed: {user_data.get('tasks_completed', 0)}
            Habits completed: {user_data.get('habits_completed', 0)}
            Productivity score: {user_data.get('productivity_score', 0)}/10
            Time spent focused: {user_data.get('time_spent_focused', 0)} hours
            Mood score: {user_data.get('mood_score', 0)}/10
            
            Provide insights in Spanish about:
            1. Strengths
            2. Areas for improvement
            3. Specific recommendations
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a productivity analyst. Provide clear, actionable insights in Spanish."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "analysis": analysis,
                "recommendations": await self._extract_recommendations(analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing productivity patterns: {e}")
            return {
                "analysis": "No se pudo analizar los patrones de productividad en este momento.",
                "recommendations": []
            }
    
    async def _extract_recommendations(self, analysis: str) -> List[str]:
        """
        Extract specific recommendations from analysis text
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract 3-5 specific, actionable recommendations from the analysis. Return as JSON array of strings."},
                    {"role": "user", "content": analysis}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            recommendations = json.loads(recommendations_text)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error extracting recommendations: {e}")
            return []
