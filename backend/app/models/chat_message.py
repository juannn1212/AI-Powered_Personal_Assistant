from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from app.database import Base


class ChatMessage(Base):
    """Metadatos de cada mensaje enviado al asistente.

    Por privacidad NO se guarda el texto de la conversación: solo la intención
    detectada, la emoción y el sentimiento, que alimentan las analíticas.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    intent = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
