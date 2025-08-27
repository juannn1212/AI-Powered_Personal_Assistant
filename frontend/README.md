# AI Personal Assistant - Frontend

Frontend de la aplicación de Asistente Personal con IA, desarrollado en React Native con Expo.

## 🚀 Características

- **Chat Inteligente**: Interacción con IA para crear tareas y hábitos
- **Gestión de Tareas**: Crear, editar, completar y eliminar tareas
- **Seguimiento de Hábitos**: Establecer y seguir hábitos diarios
- **Analytics**: Estadísticas detalladas de productividad
- **Perfil de Usuario**: Gestión completa del perfil y configuración
- **Modo Oscuro**: Soporte completo para tema oscuro y claro
- **Autenticación**: Sistema completo de login, registro y recuperación de contraseña

## 📱 Pantallas

### Autenticación
- **Login**: Inicio de sesión con email y contraseña
- **Registro**: Creación de nueva cuenta
- **Recuperar Contraseña**: Proceso de recuperación de contraseña

### Aplicación Principal
- **Chat**: Asistente IA para interacción natural
- **Tareas**: Gestión completa de tareas con filtros y estadísticas
- **Hábitos**: Seguimiento de hábitos con rachas y motivación
- **Analytics**: Dashboard con estadísticas de productividad
- **Perfil**: Configuración de usuario y preferencias

## 🛠 Tecnologías

- **React Native**: Framework principal
- **Expo**: Plataforma de desarrollo
- **React Navigation**: Navegación entre pantallas
- **AsyncStorage**: Almacenamiento local
- **Expo Linear Gradient**: Gradientes visuales
- **Ionicons**: Iconografía

## 📦 Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd frontend
```

2. **Instalar dependencias**:
```bash
npm install
```

3. **Configurar variables de entorno**:
Crear un archivo `.env` en la raíz del proyecto:
```env
API_BASE_URL=http://127.0.0.1:8000/api
```

4. **Ejecutar la aplicación**:
```bash
npm start
```

## 🔧 Configuración

### Backend
Asegúrate de que el backend esté ejecutándose en `http://127.0.0.1:8000` antes de iniciar el frontend.

### API Configuration
La configuración de la API se encuentra en `src/config/api.js`:
- `API_BASE_URL`: URL base del backend
- `API_ENDPOINTS`: Endpoints disponibles
- `getAuthHeaders`: Función para headers de autenticación

## 🎨 Temas

La aplicación soporta modo claro y oscuro con un sistema de temas completo:

### Colores Principales
- **Primary**: Color principal de la aplicación
- **Surface**: Color de fondo de tarjetas y elementos
- **Background**: Color de fondo principal
- **Text**: Color del texto principal
- **Border**: Color de bordes y separadores

### Contexto de Tema
El tema se maneja a través de `ThemeContext` y se aplica globalmente en toda la aplicación.

## 📱 Navegación

La aplicación utiliza React Navigation con:

- **Stack Navigator**: Para autenticación y navegación principal
- **Tab Navigator**: Para las pantallas principales de la aplicación

### Estructura de Navegación
```
AppNavigator
├── Auth Stack (no autenticado)
│   ├── Login
│   ├── Register
│   └── ForgotPassword
└── Main Stack (autenticado)
    └── Tab Navigator
        ├── Chat
        ├── Tareas
        ├── Hábitos
        ├── Analytics
        └── Perfil
```

## 🔐 Autenticación

El sistema de autenticación incluye:

- **Login**: Con email y contraseña
- **Registro**: Creación de nueva cuenta
- **Recuperación**: Proceso de recuperación de contraseña
- **Persistencia**: Tokens almacenados en AsyncStorage
- **Logout**: Cierre de sesión completo

## 📊 Analytics

La pantalla de analytics muestra:

- **Resumen General**: Estadísticas principales
- **Análisis de Productividad**: Horas pico, días productivos
- **Análisis de Tareas**: Tasa de completación, categorías
- **Análisis de Hábitos**: Adherencia, rachas
- **Análisis de Chat**: Interacciones con IA
- **Insights**: Recomendaciones personalizadas

## 🎯 Funcionalidades Principales

### Chat IA
- Interacción natural con el asistente
- Creación de tareas y hábitos por voz
- Sugerencias contextuales
- Análisis de sentimiento

### Gestión de Tareas
- Crear, editar, completar tareas
- Filtros por estado y prioridad
- Estadísticas en tiempo real
- Categorización automática

### Seguimiento de Hábitos
- Establecer hábitos diarios/semanales
- Seguimiento de rachas
- Consejos motivacionales
- Estadísticas de adherencia

## 🚀 Despliegue

### Expo
```bash
expo build:android
expo build:ios
```

### EAS Build
```bash
eas build --platform android
eas build --platform ios
```

## 📝 Scripts Disponibles

- `npm start`: Inicia el servidor de desarrollo
- `npm run android`: Ejecuta en Android
- `npm run ios`: Ejecuta en iOS
- `npm run web`: Ejecuta en web

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas, contacta:
- Email: soporte@aipersonalassistant.com
- GitHub Issues: [Crear un issue](https://github.com/username/repo/issues)

