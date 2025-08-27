# 🤖 AI-Powered Personal Assistant

Un asistente personal inteligente con **Machine Learning real** usando TensorFlow, React Native y FastAPI.

## 🧠 **Características Principales**

### **Inteligencia Artificial Avanzada**
- ✅ **TensorFlow Neural Networks** - Redes neuronales reales
- ✅ **Intent Classification** - Clasificación inteligente de intenciones
- ✅ **Context Awareness** - Conciencia del contexto de conversación
- ✅ **Personalized Responses** - Respuestas personalizadas
- ✅ **Sentiment Analysis** - Análisis de sentimientos
- ✅ **Smart Suggestions** - Sugerencias inteligentes

### **Funcionalidades del Asistente**
- 📝 **Creación de Tareas** desde el chat
- 🔄 **Gestión de Hábitos** inteligente
- 📊 **Análisis de Productividad** 
- 💬 **Chat Inteligente** con ML
- 🎯 **Insights Personalizados**
- ⏰ **Contexto Temporal** (mañana, tarde, noche)

## 🚀 **Tecnologías**

### **Backend (Python/FastAPI)**
- **FastAPI** - API REST moderna
- **TensorFlow** - Machine Learning
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **JWT** - Autenticación segura

### **Frontend (React Native)**
- **React Native** - App móvil multiplataforma
- **Expo** - Framework de desarrollo
- **React Navigation** - Navegación
- **AsyncStorage** - Almacenamiento local
- **Context API** - Gestión de estado

### **Machine Learning**
- **TensorFlow 2.15** - Framework de ML
- **Scikit-learn** - Algoritmos de ML
- **Neural Networks** - Redes neuronales densas
- **TF-IDF Vectorization** - Procesamiento de texto
- **Intent Classification** - Clasificación de intenciones

## 📦 **Instalación**

### **1. Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd proyectoPortafolio1
```

### **2. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

### **3. Frontend Setup**
```bash
cd frontend
npm install
```

## 🏃‍♂️ **Ejecución**

### **Backend (desde directorio backend)**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### **Frontend**
```bash
cd frontend
npx expo start
```

## 🧠 **Sistema de IA**

### **Arquitectura del Modelo**
```
Input Text → TF-IDF Vectorization → Neural Network (128-64-output) → Intent Classification
```

### **Capacidades del Modelo**
- **Entrenamiento Automático** con datos reales
- **Clasificación de Intenciones** (10+ categorías)
- **Contexto de Conversación** (últimos 20 mensajes)
- **Análisis de Estado de Ánimo**
- **Respuestas Personalizadas** según tiempo y contexto

### **Intenciones Soportadas**
- `greeting` - Saludos
- `create_task` - Crear tareas
- `create_habit` - Crear hábitos
- `view_tasks` - Ver tareas
- `view_habits` - Ver hábitos
- `productivity_tips` - Consejos de productividad
- `analytics` - Análisis y estadísticas
- `help` - Ayuda general
- `goodbye` - Despedidas

## 📱 **Funcionalidades del Chat**

### **Creación Inteligente de Tareas**
1. Usuario: "Crear una tarea"
2. IA: "¿Qué tarea quieres crear?"
3. Usuario: "Estudiar React Native"
4. IA: Crea la tarea automáticamente en la base de datos

### **Creación Inteligente de Hábitos**
1. Usuario: "Establecer un hábito"
2. IA: "¿Qué hábito quieres establecer?"
3. Usuario: "Meditar diariamente"
4. IA: Crea el hábito automáticamente en la base de datos

### **Respuestas Contextuales**
- **Saludos temporales** según la hora
- **Insights personalizados** basados en el contexto
- **Sugerencias inteligentes** según la conversación
- **Análisis de estado de ánimo** del usuario

## 🔧 **Estructura del Proyecto**

```
proyectoPortafolio1/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── tensorflow_ai_service.py  # 🧠 Sistema de ML
│   │   │   └── ai_service.py             # Servicio principal
│   │   ├── routes/
│   │   │   └── assistant.py              # Rutas del chat
│   │   ├── models/                       # Modelos de BD
│   │   └── schemas/                      # Esquemas Pydantic
│   ├── main.py                           # Punto de entrada
│   └── requirements.txt                  # Dependencias
├── frontend/
│   ├── src/
│   │   ├── screens/
│   │   │   └── ChatScreen.js             # Chat con IA
│   │   ├── context/
│   │   │   └── TasksContext.js           # Gestión de estado
│   │   └── config/
│   └── App.js
└── README.md
```

## 🎯 **Características Avanzadas**

### **Machine Learning en Tiempo Real**
- **Entrenamiento automático** al iniciar el servidor
- **Predicciones en tiempo real** para cada mensaje
- **Fallback inteligente** si el modelo falla
- **Persistencia del modelo** entrenado

### **Gestión de Estado Inteligente**
- **Contexto de conversación** mantenido
- **Sincronización automática** con la base de datos
- **Almacenamiento local** para offline
- **Actualizaciones en tiempo real**

### **Experiencia de Usuario**
- **Interfaz moderna** y responsive
- **Modo oscuro** integrado
- **Navegación fluida** entre pantallas
- **Feedback visual** para todas las acciones

## 🚀 **Próximas Mejoras**

- [ ] **Análisis de Productividad Avanzado**
- [ ] **Recomendaciones Personalizadas**
- [ ] **Integración con Calendario**
- [ ] **Notificaciones Inteligentes**
- [ ] **Análisis de Patrones de Comportamiento**

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT.

---

**¡Disfruta de tu asistente personal inteligente! 🤖✨**
