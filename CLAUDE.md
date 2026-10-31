# AI-Powered Personal Assistant — contexto para Claude

Proyecto de Juan David Martínez Ciro (github.com/juannn1212). Meta: convertirlo en un producto de IA **propio, local-first y bien hecho** (meses de trabajo, sin APIs externas de IA), con "cerebro" de memoria vectorial, y a futuro un SaaS.

## Estado actual
- **Frontend**: React Native (Expo 49) + react-native-web, en `frontend/`.
- **Backend**: FastAPI + SQLAlchemy + SQLite + JWT, en `backend/`.
- **Chat**: capa de seguridad/apoyo emocional por reglas (`backend/app/services/emotional_support.py`) + clasificador de intenciones TF-IDF/red pequeña (`tensorflow_ai_service.py`, ~60 frases fijas, respuestas enlatadas). **No razona**; es el punto a reemplazar por un LLM local.
- **Analytics**: `app/services/analytics_service.py` (cálculo puro y testeado) + rutas finas en `routes/analytics.py`.
- **Tests**: `cd backend && pip install -r requirements-dev.txt && pytest` (61 pruebas).

## Reglas del proyecto (no negociables)
1. **Sin APIs externas de IA** (nada de OpenAI/Anthropic en el producto). Modelos open-weight locales (Ollama/llama.cpp), embeddings locales.
2. **La capa de seguridad corre ANTES de cualquier modelo** y no depende de él. Crisis (ideación suicida/autolesión): respuesta fija, cálida, sin validar el deseo de morir, con recursos: **Línea 106** (salud mental, gratuita, 24 h) y **123** (emergencias). Cualquier cambio a `emotional_support.py` debe mantener y ampliar `tests/test_emotional_support.py`. En seguridad es peor un falso negativo que un falso positivo.
3. **Privacidad**: no persistir el texto de las conversaciones en analíticas (`ChatMessage` guarda solo intención/emoción/sentimiento). Los eventos de crisis no se persisten como tales. Historial en memoria por usuario, acotado.
4. La IA se presenta como asistente, **no** como psicólogo ni servicio de emergencias.
5. Las analíticas se calculan en `analytics_service.py` (puro, sin FastAPI) para poder testearlas; las rutas solo cargan datos.
6. Contrato front↔back: antes de tocar una pantalla, comprobar la forma exacta de la respuesta del endpoint (la mayoría de bugs iniciales fueron desajustes de contrato). URLs con `/` final (`/tasks/`, `/habits/`).

## Diferenciador del producto
Local/privado + memoria **transparente y controlada por el usuario** + bucle bienestar↔productividad (el asistente conecta ánimo con carga de tareas/hábitos) + español latinoamericano. Público inicial a validar: estudiantes (pendiente confirmar con Juan David).

## Arquitectura objetivo (ver docs/ROADMAP.md)
LLM local (Qwen3 / Gemma 3 / Llama 3.x / Phi-4-mini; verificar licencia y probar español) → embeddings locales (bge-m3 / e5) → PostgreSQL + pgvector → memoria por capas (episódica resumida, hechos editables por el usuario, base de conocimiento) → capa de seguridad por reglas delante → evaluación con ~50 conversaciones en español → luego LoRA.

## Convenciones
- Español en textos de usuario y comentarios; código/identificadores en inglés o como ya estén.
- Commits pequeños y en ramas `feat/…` / `fix/…`; no commitear artefactos generados (`backend/ai_model/`, `*.pkl`, `*.db` están ignorados).
- Correr `pytest` antes de cada commit.
- Backend dev: `cd backend && uvicorn main:app --reload`. Frontend: `cd frontend && npx expo start --web`.

## Pendientes conocidos
- `ChatScreen`: renderizar visualmente el mensaje de crisis (tarjeta con botón a Línea 106).
- Dockerfile / docker-compose y CI (GitHub Actions con pytest).
- Migraciones con Alembic (hoy `create_all`); `SECRET_KEY` por defecto es insegura fuera de desarrollo.
- Reemplazar `ml_models/*.pkl` y el clasificador por la arquitectura del roadmap.
