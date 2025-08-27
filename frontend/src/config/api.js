export const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  ME: '/auth/me',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  CHANGE_PASSWORD: '/auth/change-password',
  
  // Assistant
  CHAT: '/assistant/chat',
  CREATE_TASK: '/assistant/create-task',
  CREATE_HABIT: '/assistant/create-habit',
  SUGGESTIONS: '/assistant/suggestions',
  ANALYZE_MESSAGE: '/assistant/analyze-message',
  INSIGHTS: '/assistant/insights',
  
  // Tasks
  TASKS: '/tasks',
  TASK_STATS: '/tasks/stats/summary',
  
  // Habits
  HABITS: '/habits',
  HABIT_STATS: '/habits/stats/summary',
  
  // Analytics
  PRODUCTIVITY_ANALYTICS: '/analytics/productivity',
  HABITS_ANALYTICS: '/analytics/habits',
  TASKS_ANALYTICS: '/analytics/tasks',
  CHAT_ANALYTICS: '/analytics/chat',
  PRODUCTIVITY_INSIGHTS: '/analytics/insights',
  ANALYTICS_SUMMARY: '/analytics/summary',
  
  // Calendar
  CALENDAR_EVENTS: '/calendar/events',
  TODAY_EVENTS: '/calendar/today',
  WEEK_SUMMARY: '/calendar/week',
};

export const createApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}`;

export const getAuthHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`,
});

export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // Error de respuesta del servidor
    const { status, data } = error.response;
    
    switch (status) {
      case 401:
        return 'Sesión expirada. Por favor, inicia sesión nuevamente.';
      case 403:
        return 'No tienes permisos para realizar esta acción.';
      case 404:
        return 'Recurso no encontrado.';
      case 422:
        return data.detail || 'Datos inválidos.';
      case 500:
        return 'Error interno del servidor. Inténtalo más tarde.';
      default:
        return data.detail || 'Error en la solicitud.';
    }
  } else if (error.request) {
    // Error de red
    return 'Error de conexión. Verifica tu conexión a internet.';
  } else {
    // Otro tipo de error
    return error.message || 'Error inesperado.';
  }
};

